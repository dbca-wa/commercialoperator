import Vue from 'vue';
import Router from 'vue-router';
import Profile from '@/components/user/profile.vue';
import Account from '@/components/user/account.vue';
import external_routes from '@/components/external/routes';
import internal_routes from '@/components/internal/routes';
Vue.use(Router);

export default new Router({
    mode: 'history',
    routes: [
        {
            path: '/firsttime',
            name: 'first-time',
            component: Profile,
            // component: Account, // TODO: change to Account
        },
        {
            path: '/account',
            name: 'account',
            component: Account,
        },
        {
            path: '/ledger-ui/accounts',
            name: 'accounts',
            component: Account,
        },

        external_routes,
        internal_routes,
    ],
});
