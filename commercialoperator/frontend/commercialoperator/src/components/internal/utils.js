import api from './api';
import { helpers } from '@/utils/hooks';

export default {
    fetchProposal: function (id) {
        return new Promise((resolve, reject) => {
            helpers
                .fetchUrl(helpers.add_endpoint_json(api.proposals, id), {
                    emulateJSON: true,
                })
                .then(
                    (response) => {
                        resolve(response.body);
                    },
                    (error) => {
                        reject(error);
                    }
                );
        });
    },
    fetchOrganisations: function () {
        return new Promise((resolve, reject) => {
            helpers.fetchUrl(api.organisations, { emulateJSON: true }).then(
                (response) => {
                    resolve(response.body);
                },
                (error) => {
                    reject(error);
                }
            );
        });
    },
    fetchCountries: function () {
        return new Promise((resolve, reject) => {
            helpers.fetchUrl(api.countries, { emulateJSON: true }).then(
                (response) => {
                    resolve(response.body);
                },
                (error) => {
                    reject(error);
                }
            );
        });
    },
    fetchOrganisation: function (id) {
        return new Promise((resolve, reject) => {
            helpers
                .fetchUrl(helpers.add_endpoint_json(api.organisations, id), {
                    emulateJSON: true,
                })
                .then(
                    (response) => {
                        resolve(response.body);
                    },
                    (error) => {
                        reject(error);
                    }
                );
        });
    },
    fetchUser: function (id) {
        return new Promise((resolve, reject) => {
            helpers
                .fetchUrl(helpers.add_endpoint_json(api.users, id), {
                    emulateJSON: true,
                })
                .then(
                    (response) => {
                        resolve(response.body);
                    },
                    (error) => {
                        reject(error);
                    }
                );
        });
    },
    fetchOrgRequestPending: function (id) {
        return new Promise((resolve, reject) => {
            helpers
                .fetchUrl(
                    helpers.add_endpoint_json(
                        api.users,
                        id + '/pending_org_requests'
                    ),
                    { emulateJSON: true }
                )
                .then(
                    (response) => {
                        resolve(response.body);
                    },
                    (error) => {
                        reject(error);
                    }
                );
        });
    },
    fetchProfile: function () {
        return new Promise((resolve, reject) => {
            helpers.fetchUrl(api.profile, { emulateJSON: true }).then(
                (response) => {
                    resolve(response.body);
                },
                (error) => {
                    reject(error);
                }
            );
        });
    },
};
