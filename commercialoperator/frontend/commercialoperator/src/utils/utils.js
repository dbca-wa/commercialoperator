import { api_endpoints } from '@/utils/hooks';

export default {
    fetchCountries: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.countries)
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        reject(error);
                    }
                    resolve(data);
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    reject(error);
                });
        });
    },
    fetchLedgerAccount: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.account_details)
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        reject(error);
                    }
                    resolve(data);
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    reject(error);
                });
        });
    },
    fetchRequestUserID: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.request_user_id)
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        reject(error);
                    }
                    resolve(data);
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    reject(error);
                });
        });
    },
    fetchOrganisationRequests: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.organisation_request + '/linked_organisations/')
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        reject(error);
                    }
                    resolve(data);
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    reject(error);
                });
        });
    },
    fetchProfile: function () {
        return new Promise((resolve, reject) => {
            fetch(api_endpoints.profile)
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        reject(error);
                    }
                    resolve(data);
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    reject(error);
                });
        });
    },
    /**
     * Returns the linked organisation a the given ledger organisation id
     * @param {Number} id A ledger organisation id
     * @returns a Promise that resolves to the linked organisation
     */
    fetchLinkedOrganisation: function (id) {
        return new Promise((resolve, reject) => {
            const url =
                api_endpoints.organisation +
                `/linked_organisation?org_id=${id}`;
            fetch(url)
                .then(async (response) => {
                    const data = await response.json();
                    if (!response.ok) {
                        const error =
                            (data && data.message) || response.statusText;
                        console.error(error);
                        reject(error);
                    }
                    resolve(data);
                })
                .catch((error) => {
                    console.error('There was an error!', error);
                    reject(error);
                });
        });
    },
};
