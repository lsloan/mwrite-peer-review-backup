FROM httpd:2.4-alpine
ARG MPR_API_URL
ARG MPR_CSRF_COOKIE_NAME

# TODO can we remove npm stuff afterwards, or should this be done in CI?
RUN mkdir -p /tmp/build

# Only copy what's necessary for the build to avoid unnecessary rebuilds
COPY package*.json .eslint* /tmp/build/

WORKDIR /tmp/build

# Run this APK separate as it probably can be cached
RUN apk --no-cache --virtual build-deps add --update nodejs nodejs-npm   && \
    npm install

# Only copy what's necessary for the build to avoid unnecessary rebuilds
COPY build /tmp/build/build/
COPY config /tmp/build/config/
COPY frontend /tmp/build/frontend

# Build-time dependencies are all in a single RUN
# command so that useless layers aren't persisted.
RUN npm run build                                                        && \
    cp -Rv /tmp/build/dist/* /usr/local/apache2/htdocs                   && \
    rm -rf /tmp/build                                                    && \
    apk --no-cache del build-deps

WORKDIR $HTTPD_PREFIX
