<template>
    <div id="organisationOther" class="container">
        <div v-if="userError" class="alert alert-danger" role="alert">
            {{ userError }}
        </div>
        <FormSection
            :form-collapse="false"
            label="Applications"
            index="org_applications"
        >
            <ProposalDashTable
                v-if="isInternal !== null"
                ref="proposals_table"
                :level="dashboardLevel"
                :url="proposals_url"
                :org-id="orgId"
            />
        </FormSection>

        <FormSection
            :form-collapse="false"
            label="Licences"
            index="org_licences"
        >
            <ApprovalDashTable
                v-if="isInternal !== null"
                ref="approvals_table"
                :level="dashboardLevel"
                :url="approvals_url"
                :org-id="orgId"
            />
        </FormSection>

        <FormSection
            :form-collapse="false"
            label="Compliance with Requirements"
            index="org_compliances"
        >
            <ComplianceDashTable
                v-if="isInternal !== null"
                ref="compliances_table"
                :level="dashboardLevel"
                :url="compliances_url"
                :org-id="orgId"
            />
        </FormSection>
    </div>
</template>

<script>
import FormSection from '@/components/forms/section_toggle.vue';
import ProposalDashTable from '@common-utils/proposals_dashboard.vue';
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue';
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue';
import { api_endpoints, utils } from '@/utils/hooks';

export default {
    name: 'OrganisationOther',
    components: {
        FormSection,
        ProposalDashTable,
        ApprovalDashTable,
        ComplianceDashTable,
    },
    props: {
        orgId: {
            type: Number,
            default: null,
        },
    },
    data() {
        return {
            isInternal: null,
            userError: '',
        };
    },
    computed: {
        dashboardLevel() {
            return this.isInternal ? 'internal' : 'external';
        },
        proposals_url() {
            return this.isInternal
                ? api_endpoints.proposals_paginated_internal
                : api_endpoints.proposals_paginated_external;
        },
        approvals_url() {
            return api_endpoints.approvals_paginated_external;
        },
        compliances_url() {
            return this.isInternal
                ? api_endpoints.compliances_paginated_internal
                : api_endpoints.compliances_paginated_external;
        },
    },
    mounted() {
        utils
            .fetchRequestUserID()
            .then((user) => {
                this.isInternal = Boolean(user.is_internal);
            })
            .catch((error) => {
                console.error(
                    'Unable to load organisation dashboard user',
                    error
                );
                this.userError =
                    'Unable to load your user details. Please reload the page to try again.';
            });
    },
};
</script>
