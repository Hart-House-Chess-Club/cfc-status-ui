module.exports = {
  apps: [{
    name: 'cfc-status',
    script: '/root/chesstools/cfc-status-ui/venv/bin/gunicorn',
    args: '--bind 127.0.0.1:5001 --workers 2 wsgi:app',
    cwd: '/root/chesstools/cfc-status-ui',
    interpreter: 'none',
    env: {
      PORT: 5001
    },
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    error_file: '/var/log/cfc-status-error.log',
    out_file: '/var/log/cfc-status-out.log',
    log_file: '/var/log/cfc-status.log',
    time: true
  }]
};
