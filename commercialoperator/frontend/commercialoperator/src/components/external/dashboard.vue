<template>
    <div id="externalDash" class="container">
        <div class="row">
            <div class="col-sm-12">
                <div class="well well-sm">
                    <p>
                        Welcome to the {{ system_name }} dashboard.<br /><br />
                        From this page you can view existing applications,
                        create new applications,<br />
                        view current licences, apply to amend a licence, check
                        through conditions of your licence.
                    </p>
                </div>
            </div>
        </div>
        <ProposalDashTable level="external" :url="proposals_url" />
        <ApprovalDashTable level="external" :url="approvals_url" />
        <ComplianceDashTable level="external" :url="compliances_url" />
    </div>
</template>
<script>
import ProposalDashTable from '@common-utils/proposals_dashboard.vue';
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue';
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'ExternalDashboard',
    components: {
        ProposalDashTable,
        ApprovalDashTable,
        ComplianceDashTable,
    },
    data() {
        return {
            empty_list: '/api/empty_list',
            proposals_url: api_endpoints.proposals_paginated_external,
            approvals_url: api_endpoints.approvals_paginated_external,
            compliances_url: api_endpoints.compliances_paginated_external,

            system_name: api_endpoints.system_name,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {},
    methods: {},
};
</script>
