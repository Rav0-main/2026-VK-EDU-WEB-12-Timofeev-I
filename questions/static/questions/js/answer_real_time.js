function answer_real_time(questionId, userIsQuestionAuthor) {
	const sub_answer = centrifuge.newSubscription(
		`questions:${questionId}:answer`
	);
	const answersList = document.getElementById('answers-list');
	const noAnswersMessage = document.getElementById('no-answers-message');
	const currentPage = new URLSearchParams(window.location.search).get('page') || '1';

	function createAnswer(data) {
		const answer = document.createElement('div');
		answer.className = 'answer d-flex';

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
		body.appendChild(text);

		const status = document.createElement('div');
		status.className = 'd-flex flex-wrap';
		status.style.marginTop = 'auto';
		const unchecked = document.createElement('h5');
		unchecked.className = 'text-warning';
		unchecked.textContent = 'Не проверено.';
		if (userIsQuestionAuthor) {
			const setCorrectButton = document.createElement('button');
			setCorrectButton.type = 'button';
			setCorrectButton.className = 'btn btn-success btn-sm set-correct-btn';
			setCorrectButton.dataset.answer = data.answer_id;
			setCorrectButton.textContent = 'Пометить верным';
			setCorrectButton.addEventListener('click', function () {
				send_answer_set_correct(data.answer_id);
			});
			status.appendChild(setCorrectButton);
		} else {
			status.appendChild(unchecked);
		}
		body.appendChild(status);

		const voteControls = document.createElement('div');
		voteControls.className = 'vote-controls';

		const likeButton = document.createElement('button');
		likeButton.className = 'btn btn-outline-success btn-sm vote-btn';
		likeButton.dataset.answer = data.answer_id;
		likeButton.dataset.type = '1';
		likeButton.type = 'button';
		likeButton.innerHTML = '<strong>+</strong>';
		likeButton.addEventListener('click', handle_answer_like_click);

		const voteCount = document.createElement('span');
		voteCount.className = 'vote-count';
		voteCount.textContent = `${data.answer_vote_count || 0}`;

		const dislikeButton = document.createElement('button');
		dislikeButton.className = 'btn btn-outline-danger btn-sm vote-btn';
		dislikeButton.dataset.answer = data.answer_id;
		dislikeButton.dataset.type = '-1';
		dislikeButton.type = 'button';
		dislikeButton.innerHTML = '<strong>-</strong>';
		dislikeButton.addEventListener('click', handle_answer_like_click);

		voteControls.append(likeButton, voteCount, dislikeButton);
		answer.append(avatar, body, voteControls);
		return answer;
	}

	sub_answer.on('publication', function (ctx) {
		const data = ctx.data;
		const answerPage = new URL(data.question_url, window.location.origin)
			.searchParams.get('page') || '1';

		if (answerPage !== currentPage || !answersList) {
			return;
		}

		const answer = createAnswer(data);
		const answerIndex = Number(data.answer_index);
		const answersOnPage = Number(data.answers_on_page);
		const nextAnswer = answersList.children[answerIndex];

		if (nextAnswer) {
			answersList.insertBefore(answer, nextAnswer);
		} else {
			answersList.appendChild(answer);
		}

		if (noAnswersMessage) {
			noAnswersMessage.remove();
		}

		while (answersList.children.length > answersOnPage) {
			answersList.lastElementChild.remove();
		}

		const answerCount = document.querySelector('.answer-count');
		if (answerCount) {
			answerCount.textContent = Number(answerCount.textContent || 0) + 1;
		}
	}).on('subscribing', function (ctx) {
		console.log(`subscribing to answers: ${ctx.code}, ${ctx.reason}`);
	}).on('subscribed', function (ctx) {
		console.log('subscribed to answers', ctx);
	}).on('unsubscribed', function (ctx) {
		console.log(`unsubscribed from answers: ${ctx.code}, ${ctx.reason}`);
	}).subscribe();
}
