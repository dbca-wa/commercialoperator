<!-- eslint-disable vue/multi-word-component-names -->
<template lang="html">
    <div class="container">
        <div class="row">
            <div class="col-sm-12">
                <div class="row">
                    <div
                        v-if="compliance && compliance.id"
                        class="col-sm-6 offset-3 borderDecoration"
                    >
                        <strong
                            >Your document to complete a requirement of your
                            licence has been submitted</strong
                        >
                        <br />
                        <table>
                            <thead>
                                <tr>
                                    <td><strong>Compliance:</strong></td>
                                    <td>
                                        <strong>{{
                                            compliance.reference
                                        }}</strong>
                                    </td>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Date/Time:</strong></td>
                                    <td>
                                        <strong>
                                            {{
                                                formatDate(
                                                    compliance.lodgement_date
                                                )
                                            }}</strong
                                        >
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                        <div>
                            <p>Thank you for your submission.</p>
                            <p>
                                You will receive a confirmation email, and it
                                will show up on your account if the document
                                meets the requirement.
                            </p>
                            <p>
                                You will receive a notification email if there
                                is any incomplete information or documents
                                missing.
                            </p>
                        </div>
                        <router-link
                            :to="{ name: 'external-proposals-dash' }"
                            style="margin-top: 15px"
                            class="btn btn-primary"
                            >Back to home</router-link
                        >
                    </div>
                    <div v-else class="col-sm-6 offset-3 borderDecoration">
                        <strong
                            >Sorry it looks like there isn't any compliance
                            currently in your session.</strong
                        >
                        <br /><router-link
                            :to="{ name: 'external-proposals-dash' }"
                            style="margin-top: 15px"
                            class="btn btn-primary"
                            >Back to home</router-link
                        >
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script>
import { api_endpoints, helpers } from '@/utils/hooks';

export default {
    components: {},
    beforeRouteEnter: function (to, from, next) {
        next((vm) => {
            vm.fetchCompliance(to.params.compliance_id);
        });
    },
    data: function () {
        return {
            compliance: {},
        };
    },
    computed: {},
    mounted: function () {
        let vm = this;
        vm.form = document.forms.new_compliance;
    },
    methods: {
        formatDate: function (data) {
            return data ? moment(data).format('DD/MM/YYYY HH:mm:ss') : '';
        },
        fetchCompliance: async function (compliance_id) {
            let vm = this;
            const response = await fetch(
                helpers.add_endpoint_json(
                    api_endpoints.compliances,
                    compliance_id
                )
            );
            const resData = await response.json();
            vm.compliance = Object.assign({}, resData);
        },
    },
};
</script>

<style lang="css" scoped>
.borderDecoration {
    border: 1px solid;
    border-radius: 5px;
    padding: 50px;
    margin-top: 70px;
}
</style>
