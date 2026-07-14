<template>
    <div id="organisationOther" class="container">
        <FormSection
            :form-collapse="false"
            label="Applications"
            index="org_applications"
        >
            <ProposalDashTable
                ref="proposals_table"
                level="external"
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
                ref="approvals_table"
                level="external"
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
                ref="compliances_table"
                level="external"
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
import { api_endpoints } from '@/utils/hooks';

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
            proposals_url: api_endpoints.proposals_paginated_external,
            approvals_url: api_endpoints.approvals_paginated_external,
            compliances_url: api_endpoints.compliances_paginated_external,
        };
    },
};
</script>

