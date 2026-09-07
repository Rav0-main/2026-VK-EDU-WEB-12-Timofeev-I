function centrifuge_connect(user_jwt_token)
{
    const centrifuge = new Centrifuge("ws://127.0.0.1:8000/connection/websocket", {
        token: user_jwt_token
    });

    centrifuge.on('connecting', function (ctx) {
        console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
    }).on('connected', function (ctx) {
        console.log(`connected over ${ctx.transport}`);
    }).on('disconnected', function (ctx) {
        console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
    }).connect();

    return centrifuge;
}