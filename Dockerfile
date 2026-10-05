FROM nginx:alpine

WORKDIR /usr/share/nginx/html

RUN rm -rf ./*

COPY presentacion.html index.html
COPY presentacion2.html ./
COPY presentacion3.html ./
COPY favicon.ico ./
COPY ecosistema-digital.jpg ./
COPY image.png ./
COPY diagrama_alb_fargate.png ./

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]
