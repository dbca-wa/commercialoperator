import Vue from 'vue';
import Router from 'vue-router';
import Account from '@/components/user/account.vue';
import Organisation from '@/components/common/organisation.vue';
import external_routes from '@/components/external/routes';
import internal_routes from '@/components/internal/routes';
Vue.use(Router);

export default new Router({
    mode: 'history',
    routes: [
        {
            path: '/firsttime',
            name: 'first-time',
            component: Account,
        },
        {
            path: '/ledger-ui/accounts',
            name: 'account',
            component: Account,
        },
        {
            path: '/ledger-ui/organisation/:org_id',
            name: 'organisation',
            component: Organisation,
        },
        external_routes,
        internal_routes,
    ],
});
