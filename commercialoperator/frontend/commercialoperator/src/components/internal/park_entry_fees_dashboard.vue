<template>
    <div id="internalDash" class="container">
        <div v-if="one_row_per_park">
            <ParkBookingDash level="internal" />
        </div>
        <div v-else>
            <PaymentDash level="internal" />
        </div>
    </div>
</template>
<script>
import ParkBookingDash from '@common-utils/parkbookings_dashboard.vue';
import PaymentDash from '@common-utils/payments_dashboard.vue';
import { api_endpoints } from '@/utils/hooks';
export default {
    name: 'ParkEntryFeesDashboard',
    components: {
        ParkBookingDash,
        PaymentDash,
    },
    data() {
        return {
            profile: {},
            one_row_per_park: false,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {
        this.fetchProfile();
    },
    methods: {
        fetchProfile: function () {
            let vm = this;
            vm.$http.get(api_endpoints.profile).then(
                (response) => {
                    vm.profile = response.body;
                    if (vm.profile.system_settings == null) {
                        vm.one_row_per_park = false;
                    } else {
                        vm.one_row_per_park =
                            vm.profile.system_settings.one_row_per_park;
                    }
                },
                (error) => {
                    console.log(error);
                }
            );
        },
    },
};
</script>
