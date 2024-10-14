<template id="comms_logs">
    <div class="row">
        <div class="panel panel-default">
            <div class="panel-heading">Logs</div>
            <div class="panel-body panel-collapse">
                <div class="row">
                    <div class="col-sm-12">
                        <strong>Communications</strong><br />
                        <div class="row">
                            <div class="col-sm-5">
                                <a
                                    ref="showCommsBtn"
                                    tabindex="2"
                                    class="actionBtn"
                                    >Show</a
                                >
                            </div>
                            <template v-if="!disable_add_entry">
                                <div class="col-sm-1">
                                    <span>|</span>
                                </div>
                                <div class="col-sm-5">
                                    <a
                                        ref="addCommsBtn"
                                        class="actionBtn pull-right"
                                        @click="addComm()"
                                        >Add Entry</a
                                    >
                                </div>
                            </template>
                        </div>
                    </div>
                    <div class="col-sm-12 top-buffer-s">
                        <strong>Actions</strong><br />
                        <a ref="showActionBtn" tabindex="2" class="actionBtn"
                            >Show</a
                        >
                    </div>
                </div>
            </div>
        </div>
        <AddCommLog ref="add_comm" :url="comms_add_url" />
    </div>
</template>
<script>
import AddCommLog from './add_comm_log.vue';
export default {
    name: 'CommsLogSection',
    components: {
        AddCommLog,
    },
    props: {
        // eslint-disable-next-line vue/prop-name-casing
        comms_url: {
            type: String,
            required: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        logs_url: {
            type: String,
            required: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        comms_add_url: {
            type: String,
            required: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        disable_add_entry: {
            type: Boolean,
            default: true,
        },
        // eslint-disable-next-line vue/prop-name-casing
        is_user_log: {
            type: Boolean,
            default: false,
        },
    },
    data() {
        let vm = this;
        return {
            dateFormat: 'DD/MM/YYYY HH:mm:ss',
            actionsTable: null,
            popoversInitialised: false,
            actionsDtOptions: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[3, 'desc']], // order the non-formatted date as a hidden column
                dom:
                    "<'row'<'col-sm-5'l><'col-sm-6'f>>" +
                    "<'row'<'col-sm-12'tr>>" +
                    "<'row'<'col-sm-5'i><'col-sm-7'p>>",
                processing: true,
                ajax: {
                    url: vm.logs_url,
                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'who',
                        orderable: false,
                    },
                    {
                        data: 'what',
                        orderable: false,
                    },
                    {
                        data: 'when',
                        orderable: false,
                        // eslint-disable-next-line no-unused-vars
                        mRender: function (data, type, full) {
                            return moment(data).format(vm.dateFormat);
                        },
                    },
                    {
                        title: 'Created',
                        data: 'when',
                        visible: false,
                    },
                ],
            },
            commsDtOptions: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                deferRender: true,
                autowidth: true,
                order: [[8, 'desc']], // order the non-formatted date as a hidden column
                processing: true,
                ajax: {
                    url: vm.comms_url,
                    dataSrc: '',
                },
                columns: [
                    {
                        title: 'Date',
                        data: 'created',
                        render: function (date) {
                            return moment(date).format(vm.dateFormat);
                        },
                    },
                    {
                        title: 'Type',
                        data: 'id',
                        mRender: function (data, type, full) {
                            return vm.is_user_log ? full.log_type : full.type;
                        },
                    },
                    {
                        title: 'To',
                        data: 'to',
                        render: function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' ',
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template(
                                    '<a href="#" ' +
                                        'role="button" ' +
                                        'data-bs-toggle="popover" ' +
                                        'data-bs-trigger="click" ' +
                                        'data-bs-placement="top auto"' +
                                        'data-bs-html="true" ' +
                                        'data-bs-content="<%= text %>" ' +
                                        '>more</a>'
                                );
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value,
                                });
                            }

                            return result;
                        },
                    },
                    {
                        title: 'CC',
                        data: 'cc',
                        render: function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' ',
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template(
                                    '<a href="#" ' +
                                        'role="button" ' +
                                        'data-bs-toggle="popover" ' +
                                        'data-bs-trigger="click" ' +
                                        'data-bs-placement="top auto"' +
                                        'data-bs-html="true" ' +
                                        'data-bs-content="<%= text %>" ' +
                                        '>more</a>'
                                );
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value,
                                });
                            }

                            return result;
                        },
                    },
                    {
                        title: 'From',
                        data: 'fromm',
                        render: vm.commaToNewline,
                    },
                    {
                        title: 'Subject/Desc.',
                        data: 'subject',
                        render: function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 25,
                                    omission: ellipsis,
                                    separator: ' ',
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template(
                                    '<a href="#" ' +
                                        'role="button" ' +
                                        'data-bs-toggle="popover" ' +
                                        'data-bs-trigger="click" ' +
                                        'data-bs-placement="top auto"' +
                                        'data-bs-html="true" ' +
                                        'data-bs-content="<%= text %>" ' +
                                        '>more</a>'
                                );
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value,
                                });
                            }

                            return result;
                        },
                    },
                    {
                        title: 'Text',
                        data: 'text',
                        render: function (value) {
                            var ellipsis = '...',
                                truncated = _.truncate(value, {
                                    length: 100,
                                    omission: ellipsis,
                                    separator: ' ',
                                }),
                                result = '<span>' + truncated + '</span>',
                                popTemplate = _.template(
                                    '<a href="#" ' +
                                        'role="button" ' +
                                        'data-bs-toggle="popover" ' +
                                        'data-bs-trigger="click" ' +
                                        'data-bs-placement="top auto"' +
                                        'data-bs-html="true" ' +
                                        'data-bs-content="<%= text %>" ' +
                                        '>more</a>'
                                );
                            if (_.endsWith(truncated, ellipsis)) {
                                result += popTemplate({
                                    text: value,
                                });
                            }

                            return result;
                        },
                    },
                    {
                        title: 'Documents',
                        data: 'documents',
                        render: function (values) {
                            var result = '';
                            _.forEach(values, function (value) {
                                // We expect an array [docName, url]
                                // if it's a string it is the url
                                var docName = '',
                                    url = '';
                                if (_.isArray(value) && value.length > 1) {
                                    docName = value[0];
                                    url = value[1];
                                }
                                if (typeof s === 'string') {
                                    url = value;
                                    // display the first  chars of the filename
                                    docName = _.last(value.split('/'));
                                    docName = _.truncate(docName, {
                                        length: 18,
                                        omission: '...',
                                        separator: ' ',
                                    });
                                }
                                result +=
                                    '<a href="' +
                                    url +
                                    '" target="_blank"><p>' +
                                    docName +
                                    '</p></a><br>';
                            });
                            return result;
                        },
                    },
                    {
                        title: 'Created',
                        data: 'created',
                        visible: false,
                    },
                ],
            },
            commsTable: null,
        };
    },
    computed: {},
    watch: {},
    mounted: function () {
        let vm = this;
        this.$nextTick(() => {
            vm.initialisePopovers();
        });
    },
    methods: {
        initialiseCommLogs: function (vm_uid, ref, datatable_options, table) {
            // To allow table elements (ref: https://getbootstrap.com/docs/5.1/getting-started/javascript/#sanitizer)
            var myDefaultAllowList = bootstrap.Tooltip.Default.allowList;

            myDefaultAllowList.table = [];
            let vm = this;
            let commsLogId = 'comms-log-table' + vm.uuid;
            let popover_name = 'popover-' + vm.uuid + '-comms';
            let popover_elem = $(vm.$refs.showCommsBtn)[0];
            let my_content =
                '<table id="' +
                commsLogId +
                '" class="hover table table-striped table-bordered dt-responsive" cellspacing="0"></table>';
            let my_template =
                '<div class="popover ' +
                popover_name +
                '" role="tooltip"><div class="popover-arrow" style="top:110px;"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>';
            new bootstrap.Popover(popover_elem, {
                sanitize: false,
                html: true,
                content: my_content,
                template: my_template,
                title: 'Communication logs',
                container: 'body',
                placement: 'auto',
                trigger: 'click',
            });

            popover_elem.addEventListener('inserted.bs.popover', function () {
                table = $('#' + commsLogId).DataTable(datatable_options);

                // activate popover when table is drawn.
                table.on('draw.dt', function () {
                    var $tablePopover = $(this).find(
                        '[data-bs-toggle="popover"]'
                    );
                    if ($tablePopover.length > 0) {
                        // $tablePopover.popover();
                        // the next line prevents from scrolling up to the top after clicking on the popover.
                        $($tablePopover).on('click', function (e) {
                            e.preventDefault();
                            return true;
                        });
                    }
                });
            });
            popover_elem.addEventListener('shown.bs.popover', function () {
                var el = popover_elem;
                // eslint-disable-next-line no-unused-vars
                var popoverheight = parseInt($('.' + popover_name).height());

                var popover_bounding_top = parseInt(
                    $('.' + popover_name)[0].getBoundingClientRect().top
                );
                // eslint-disable-next-line no-unused-vars
                var popover_bounding_bottom = parseInt(
                    $('.' + popover_name)[0].getBoundingClientRect().bottom
                );

                var el_bounding_top = parseInt(
                    $(el)[0].getBoundingClientRect().top
                );
                // eslint-disable-next-line no-unused-vars
                var el_bounding_bottom = parseInt(
                    $(el)[0].getBoundingClientRect().top
                );

                var diff = el_bounding_top - popover_bounding_top;

                // eslint-disable-next-line no-unused-vars
                var position = parseInt($('.' + popover_name).position().top);
                // eslint-disable-next-line no-unused-vars
                var pos2 = parseInt($(el).position().top) - 5;

                var x = diff + 5;
                $('.' + popover_name)
                    .children('.arrow')
                    .css('top', x + 'px');
            });
        },
        // eslint-disable-next-line no-unused-vars
        initialiseActionLogs: function (vm_uid, ref, datatable_options, table) {
            // To allow table elements (ref: https://getbootstrap.com/docs/5.1/getting-started/javascript/#sanitizer)
            var myDefaultAllowList = bootstrap.Tooltip.Default.allowList;
            myDefaultAllowList.table = [];

            let vm = this;
            let actionLogId = 'actions-log-table' + vm.uuid;
            let popover_name = 'popover-' + vm.uuid + '-logs';
            let popover_elem = $(vm.$refs.showActionBtn)[0];
            let my_content =
                '<table id="' +
                actionLogId +
                '" class="hover table table-striped table-bordered dt-responsive" cellspacing="0" width="100%"></table>';
            let my_template =
                '<div class="popover ' +
                popover_name +
                '" role="tooltip"><div class="popover-arrow" style="top:110px;"></div><h3 class="popover-header"></h3><div class="popover-body"></div></div>';
            new bootstrap.Popover(popover_elem, {
                html: true,
                content: my_content,
                template: my_template,
                title: 'Action logs',
                container: 'body',
                placement: 'auto',
                trigger: 'click',
            });

            popover_elem.addEventListener('inserted.bs.popover', function () {
                table = $('#' + actionLogId).DataTable(datatable_options);
            });
            popover_elem.addEventListener('shown.bs.popover', function () {
                var el = popover_elem;
                // eslint-disable-next-line no-unused-vars
                var popoverheight = parseInt($('.' + popover_name).height());

                var popover_bounding_top = parseInt(
                    $('.' + popover_name)[0].getBoundingClientRect().top
                );
                // eslint-disable-next-line no-unused-vars
                var popover_bounding_bottom = parseInt(
                    $('.' + popover_name)[0].getBoundingClientRect().bottom
                );

                var el_bounding_top = parseInt(
                    $(el)[0].getBoundingClientRect().top
                );
                // eslint-disable-next-line no-unused-vars
                var el_bounding_bottom = parseInt(
                    $(el)[0].getBoundingClientRect().top
                );

                var diff = el_bounding_top - popover_bounding_top;

                // eslint-disable-next-line no-unused-vars
                var position = parseInt($('.' + popover_name).position().top);
                // eslint-disable-next-line no-unused-vars
                var pos2 = parseInt($(el).position().top) - 5;

                var x = diff + 5;
                $('.' + popover_name)
                    .children('.arrow')
                    .css('top', x + 'px');
            });
        },
        initialisePopovers: function () {
            if (!this.popoversInitialised) {
                this.initialiseActionLogs(
                    this._uid,
                    this.$refs.showActionBtn,
                    this.actionsDtOptions,
                    this.actionsTable
                );
                this.initialiseCommLogs(
                    '-internal-proposal-' + this._uid,
                    this.$refs.showCommsBtn,
                    this.commsDtOptions,
                    this.commsTable
                );
                this.popoversInitialised = true;
            }
        },
        addComm() {
            this.$refs.add_comm.isModalOpen = true;
        },
    },
};
</script>
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
</style>
