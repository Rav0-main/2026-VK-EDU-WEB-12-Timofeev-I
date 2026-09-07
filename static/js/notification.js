function truncate(str, length) {
    if (str.length > length) {
        return str.slice(0, length) + '...';
    }
    return str;
}
function show_notification(title, text, link, duration) {
    const container = document.getElementById('notifContainer');
    
    const notif = document.createElement('div');
    notif.className = 'notification';
    notif.innerHTML = `
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        <strong>${title}</strong>
        <p style="margin:5px 0 0">${text}</p>
        <a style="link-success" href=${link}>Посмотреть ответ можно тут</a>
        <div class="timer-bar" style="width:100%"></div>
    `;
    
    container.appendChild(notif);
    
    let timeLeft = duration;
    const timerBar = notif.querySelector('.timer-bar');
    
    const interval = setInterval(() => {
        timeLeft -= 0.1;
        timerBar.style.width = (timeLeft / duration) * 100 + '%';
    }, 100);
    
    setTimeout(() => {
        clearInterval(interval);
        notif.remove();
    }, duration * 1000);
}