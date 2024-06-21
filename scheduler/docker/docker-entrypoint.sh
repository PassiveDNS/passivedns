#!/bin/bash
set -euo pipefail
#!/bin/bash
set -e

if [[ "$1" =~ "scheduler" ]]; then
    celery -A tasks worker --loglevel=info
fi

if [[ "$1" =~ "shell" ]]; then
    /bin/bash
fi

exec "$@"
