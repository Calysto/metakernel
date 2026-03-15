# JupyterHub Deployment

This page describes how to deploy MetaKernel-based kernels on
[JupyterHub](https://jupyterhub.readthedocs.io/) and how to configure a
reverse proxy (Apache or nginx) in front of JupyterHub.

## Installing a kernel for all users

On a shared JupyterHub server you typically want to install the kernel
system-wide so that every user can select it:

```bash
# as root or with sudo
python -m my_kernel install --sys-prefix
```

If you run JupyterHub inside a conda environment, use `--sys-prefix` to
install into that environment's prefix. The `--user` flag is appropriate
for single-user testing but **will not** make the kernel visible to other
JupyterHub users.

## Kernel discovery

JupyterHub spawns a separate single-user server for each user. The kernel
spec (installed under a shared prefix) is found automatically as long as
the `JUPYTER_PATH` environment variable includes the prefix's data
directory. No additional configuration is usually needed.

## Reverse proxy configuration

JupyterHub must be reached through a single public URL (e.g.
`https://hub.example.com/jupyter`). Both Apache and nginx need special
settings to proxy WebSocket connections, which the Jupyter protocol relies
on for kernel communication.

### Apache (mod_proxy / mod_proxy_wstunnel)

```apache
<VirtualHost *:443>
    ServerName hub.example.com

    SSLEngine on
    SSLCertificateFile    /etc/ssl/certs/hub.crt
    SSLCertificateKeyFile /etc/ssl/private/hub.key

    # Enable the required proxy modules:
    #   LoadModule proxy_module          modules/mod_proxy.so
    #   LoadModule proxy_http_module     modules/mod_proxy_http.so
    #   LoadModule proxy_wstunnel_module modules/mod_proxy_wstunnel.so

    ProxyPreserveHost On

    # WebSocket upgrade (kernel channels, terminals)
    RewriteEngine On
    RewriteCond %{HTTP:Upgrade} websocket [NC]
    RewriteRule /jupyter/(.*) ws://127.0.0.1:8000/jupyter/$1 [P,L]

    # Standard HTTP
    ProxyPass        /jupyter/ http://127.0.0.1:8000/jupyter/
    ProxyPassReverse /jupyter/ http://127.0.0.1:8000/jupyter/

    # Required headers
    RequestHeader set X-Scheme https
    RequestHeader set X-Forwarded-Proto https
</VirtualHost>
```

Set the matching base URL in your `jupyterhub_config.py`:

```python
c.JupyterHub.base_url = '/jupyter/'
```

### nginx

```nginx
server {
    listen 443 ssl;
    server_name hub.example.com;

    ssl_certificate     /etc/ssl/certs/hub.crt;
    ssl_certificate_key /etc/ssl/private/hub.key;

    location /jupyter/ {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";

        # Increase timeouts for long-running kernels
        proxy_read_timeout 86400;
    }
}
```

## Jigsaw magic under JupyterHub

The `%jigsaw` magic embeds a Blockly visual editor in an IFrame. In a
JupyterHub environment the IFrame is served from the user's file space
(`/user/{name}/files/workspace.html`), which has a **different origin**
from the notebook page. Modern browsers block direct `window.parent`
property access across origins, causing a `SecurityError`.

MetaKernel handles this automatically by:

1. **Replacing `window.parent.*` property access with `postMessage`** — the
   iframe sends structured messages to the parent page instead of accessing
   its DOM directly.
1. **Embedding saved workspace XML in the HTML** — instead of fetching the
   `.xml` file via XHR (which is also blocked from a cross-origin or
   sandboxed iframe), the XML is serialised into a JavaScript variable
   inside the generated HTML file at magic-run time.
1. **WebSocket kernel execution fallback** — when the classic
   `IPython.notebook` or JupyterLab JS APIs are not reachable, the helper
   falls back to discovering the kernel via the REST `/api/sessions`
   endpoint and connects directly over WebSocket. The base URL is read
   from the `jupyter-config-data` element injected by the server, so the
   correct JupyterHub-prefixed path is used automatically.

No special configuration is required — these fixes are applied every time
`%jigsaw` is executed.

### Known limitations

- The `%jigsaw` magic writes the generated `.html` and `.xml` workspace
  files to the **current working directory** of the kernel. On JupyterHub
  this is typically the user's home directory, so the files are accessible
  through the file browser.
- Very restrictive Content Security Policies set by the proxy (e.g.
  `frame-src 'self'`) may still prevent the IFrame from loading. If you
  control the proxy, allow `frame-src` for the JupyterHub origin.

## Troubleshooting

**Kernel does not appear in the launcher**
: Check that the kernel spec is installed under a prefix that is on
`JUPYTER_PATH`. Run `jupyter kernelspec list` as the spawned user to
verify.

**`%jigsaw` shows a blank iframe / SecurityError in the browser console**
: Make sure you are running a recent version of MetaKernel (≥ 1.0).
Earlier versions wrote HTML that accessed `window.parent` directly, which
is blocked across origins.

**WebSocket connections fail through the proxy**
: Ensure `mod_proxy_wstunnel` (Apache) or `proxy_http_version 1.1` +
`Upgrade`/`Connection` headers (nginx) are configured. WebSocket
upgrades require explicit proxy support.

**404 on `/jupyter/` after setting `base_url`**
: The trailing slash in `c.JupyterHub.base_url = '/jupyter/'` is required.
The proxy `ProxyPass` / `location` block must use the same path prefix.
