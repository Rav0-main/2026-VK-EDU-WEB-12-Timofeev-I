function subscribeToChannel(channel) {
	const subscription = centrifuge.newSubscription(channel);

	subscription.on('subscribing', function (ctx) {
		console.log(`subscribing to channel ${channel}: ${ctx.code}, ${ctx.reason}`);
	}).on('subscribed', function () {
		console.log(`subscribed to channel ${channel}`);
	}).on('unsubscribed', function (ctx) {
		console.log(`unsubscribed from channel ${channel}: ${ctx.code}, ${ctx.reason}`);
	});

	return subscription;
}

function answer_new_vote_count(answerId) {
	const subscription = subscribeToChannel(`answers:${answerId}:like`);

	subscription.on('publication', function (ctx) {
		const answer = document.getElementById(`answer-${ctx.data.answer_id}`);
		if (!answer) {
			return;
		}

		const voteCount = answer.querySelector('.vote-count');
		if (voteCount) {
			voteCount.textContent = ctx.data.vote_count;
		}
	}).subscribe();
}

function answer_set_correct(answerId) {
	const subscription = subscribeToChannel(`answers:${answerId}:correct`);

	subscription.on('publication', function (ctx) {
		const answer = document.getElementById(`answer-${ctx.data.answer_id}`);
		const status = answer && answer.querySelector('.answer-status');
		if (!answer || !status) {
			return;
		}

		answer.classList.add('correct-answer');
		status.replaceChildren();

		const correctLabel = document.createElement('h5');
		correctLabel.className = 'text-success';
		correctLabel.textContent = 'Верный.';
		status.appendChild(correctLabel);
	}).subscribe();
}

function createAnswerVoteButton(answerId, type, className, symbol) {
	const button = document.createElement('button');
	button.className = `btn ${className} btn-sm vote-btn`;
	button.type = 'button';
	button.dataset.answer = answerId;
	button.dataset.type = type;
	button.innerHTML = `<strong>${symbol}</strong>`;
	button.addEventListener('click', handle_answer_like_click);
	return button;
}

function createAnswerStatus(answerId, userIsQuestionAuthor) {
	const status = document.createElement('div');
	status.className = 'd-flex flex-wrap answer-status';
	status.style.marginTop = 'auto';

	if (userIsQuestionAuthor) {
		const button = document.createElement('button');
		button.type = 'button';
		button.className = 'btn btn-success btn-sm set-correct-btn';
		button.dataset.answer = answerId;
		button.textContent = 'Пометить верным';
		button.addEventListener('click', function () {
			send_answer_set_correct(answerId);
		});
		status.appendChild(button);
		return status;
	}

	const label = document.createElement('h5');
	label.className = 'text-warning';
	label.textContent = 'Не проверено.';
	status.appendChild(label);
	return status;
}

function createAnswer(data, userIsQuestionAuthor) {
	const answer = document.createElement('div');
	answer.className = 'answer d-flex';
	answer.id = `answer-${data.answer_id}`;

	const avatar = document.createElement('div');
	avatar.className = 'answer-avatar';
	const image = document.createElement('img');
	image.className = 'answer-avatar img-fluid';
	image.src = data.author_avatar_url || '#';
	image.alt = '';
	const author = document.createElement('div');
	author.className = 'answer-author text-center text-break';
	author.textContent = data.author_nickname || '';
	avatar.append(image, author);

	const body = document.createElement('div');
	body.className = 'flex-grow-1';
	body.style.cssText = 'margin-left: 0.5rem; margin-right: 0.5rem; display: flex; flex-direction: column;';
	const text = document.createElement('div');
	text.className = 'answer-text';
	text.textContent = data.content || '';
	body.append(text, createAnswerStatus(data.answer_id, userIsQuestionAuthor));

	const voteControls = document.createElement('div');
	voteControls.className = 'vote-controls';
	const likeButton = createAnswerVoteButton(data.answer_id, '1', 'btn-outline-success', '+');
	const voteCount = document.createElement('span');
	voteCount.className = 'vote-count';
	voteCount.textContent = data.answer_vote_count || 0;
	const dislikeButton = createAnswerVoteButton(data.answer_id, '-1', 'btn-outline-danger', '-');
	voteControls.append(likeButton, voteCount, dislikeButton);

	answer.append(avatar, body, voteControls);
	return answer;
}

function answer_real_time(questionId, userIsQuestionAuthor) {
	const answersList = document.getElementById('answers-list');
	const noAnswersMessage = document.getElementById('no-answers-message');
	const currentPage = new URLSearchParams(window.location.search).get('page') || '1';
	if (!answersList) {
		return;
	}

	function subscribeToAnswerUpdates(answerId) {
		answer_new_vote_count(answerId);
		answer_set_correct(answerId);
	}

	answersList.querySelectorAll('[id^="answer-"]').forEach(function (answer) {
		subscribeToAnswerUpdates(answer.id.replace('answer-', ''));
	});

	const subscription = subscribeToChannel(`questions:${questionId}:answer`);
	subscription.on('publication', function (ctx) {
		const data = ctx.data;
		const answerPage = new URL(data.question_url, window.location.origin)
			.searchParams.get('page') || '1';

		if (answerPage !== currentPage || !answersList) {
			return;
		}

		const answer = createAnswer(data, userIsQuestionAuthor);
		const nextAnswer = answersList.children[Number(data.answer_index)];
		if (nextAnswer) {
			answersList.insertBefore(answer, nextAnswer);
		} else {
			answersList.appendChild(answer);
		}

		subscribeToAnswerUpdates(data.answer_id);
		if (noAnswersMessage) {
			noAnswersMessage.remove();
		}

		while (answersList.children.length > Number(data.answers_on_page)) {
			answersList.lastElementChild.remove();
		}
	}).subscribe();
}
