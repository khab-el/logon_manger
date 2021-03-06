#!/bin/bash

export $(xargs < /app/config/logon.cfg)
echo 'export $(xargs < /app/config/logon.cfg)' >> $HOME/.bashrc

cat > templates/button.html << EOL
<style>
body {
    margin: 0;            /* Reset default margin */
}

#bt1 {
    position: absolute;
    height: 48px;
    min-width: 48px;
    right: 15px;
    top: 0px;
    background: white;
    border: none;
    border-radius: 0;
}

a:hover, button, [role='button'] {
    cursor: pointer;
}

.holder {
    width: 100%;
    height: 100%;
    position: relative;
}

iframe {
    display: block;       /* iframes are inline by default */
    background: #000;
    border: none;         /* Reset default border */
    height: 100vh;        /* Viewport-relative units */
    width: 100vw;
}
</style>
<div class="holder">
    <iframe src="/kibana/app/kibana" height="100%" width="100%"></iframe>
    <button id="bt1" onclick="window.location.href='${BASE_URL}/logout'">Logout</button>
</div>
EOL

gunicorn -w $GUNICORN_WORKER -b $SERVER_HOST:$SERVER_PORT --log-file $LOG_DIR/logon_manager_$(date +"%d%m%Y_%H-%M").log app:app
# python3 app.py