// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue';
import resource from 'vue-resource';
import App from './App';
import router from './router';
import 'bootstrap';
import helpers from '@/utils/helpers';
import { extendMoment } from 'moment-range';

// require('datatables.net');
// require('datatables.net-bs')();
// require('datatables.net-responsive-bs')(window, $);
// require('datatables.net-buttons/js/dataTables.buttons.js')(window, $);
// require('datatables.net-buttons/js/buttons.html5.js')(window, $, jsZip);

import 'datatables.net';
import 'datatables.net-bs';
import 'datatables.net-buttons';
import 'datatables.net-responsive';
// import 'datatables.net-buttons-bs';
import 'datatables.net-responsive-bs';
import 'datatables.net-buttons/js/dataTables.buttons.js';
import 'datatables.net-buttons/js/buttons.html5.js';

import jsZip from 'jszip';
window.JSZip = jsZip;

import 'select2';
import 'jquery-validation';

import 'sweetalert2/dist/sweetalert2.css';
import '@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css';
import 'select2/dist/css/select2.min.css';
import 'select2-bootstrap-5-theme/dist/select2-bootstrap-5-theme.min.css';
import '@/../node_modules/datatables.net-bs/css/dataTables.bootstrap.min.css';
import '@/../node_modules/datatables.net-responsive-bs/css/responsive.bootstrap.min.css';

// eslint-disable-next-line no-unused-vars
// import hooks from './packages';
import api_endpoints from './api';

require('@/../node_modules/@fortawesome/fontawesome-free/css/all.min.css');
require('@/../node_modules/datatables.net-bs/css/dataTables.bootstrap.min.css');

extendMoment(moment);

Vue.config.devtools = true;
Vue.config.productionTip = false;
Vue.use(resource);

// Add CSRF Token to every request
Vue.http.interceptors.push(function (request, next) {
    // modify headers
    if (request.url != api_endpoints.countries) {
        request.headers.set('X-CSRFToken', helpers.getCookie('csrftoken'));
    }

    // continue to next interceptor
    next();
});

new Vue({
    el: '#app',
    router,
    components: {
        App,
    },
    template: '<App/>',
});
