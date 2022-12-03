FROM fholzer/nginx-brotli

COPY deployment/nginx/nginx.conf /etc/nginx/conf.d/default.conf
ENTRYPOINT ["nginx"]
CMD ["-g", "daemon off;"]
