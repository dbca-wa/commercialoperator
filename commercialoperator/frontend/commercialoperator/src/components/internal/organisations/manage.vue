<template>
    <div id="internalOrgInfo" class="container-fluid">
        <div class="row">
            <div class="col-md-10 col-md-offset-1">
                <div class="row">
                    <h3>
                        {{ org.organisation_name }} - {{ org.organisation_abn }}
                    </h3>
                    <div class="col-md-3">
                        <CommsLogs
                            :comms_url="comms_url"
                            :logs_url="logs_url"
                            :comms_add_url="comms_add_url"
                            :disable_add_entry="false"
                        />
                    </div>
                    <div class="col-md-1"></div>
                    <div class="col-md-8">
                        <ul class="nav nav-pills mb-3" role="tablist">
                            <li class="nav-item">
                                <a
                                    id="pills-details-tab"
                                    data-toggle="tab"
                                    class="nav-link active"
                                    data-bs-toggle="pill"
                                    :href="'#' + dTab"
                                    role="tab"
                                    :aria-controls="dTab"
                                    aria-selected="true"
                                    >Details</a
                                >
                            </li>
                            <li class="nav-item">
                                <a
                                    id="pills-other-tab"
                                    data-toggle="tab"
                                    class="nav-link"
                                    data-bs-toggle="pill"
                                    :href="'#' + oTab"
                                    role="tab"
                                    :aria-controls="oTab"
                                    aria-selected="false"
                                    >Other</a
                                >
                            </li>
                        </ul>
                        <div class="tab-content">
                            <div
                                :id="dTab"
                                class="tab-pane fade active show"
                                role="tabpanel"
                                aria-labelledby="pills-details-tab"
                            >
                                <div class="row">
                                    <div class="col-sm-12">
                                        <div class="panel panel-default">
                                            <FormSection
                                                :form-collapse="false"
                                                label="Organisation Details"
                                                index="organisation_details"
                                                subtitle=""
                                            >
                                                <form
                                                    class="form-horizontal"
                                                    name="personal_form"
                                                    method="post"
                                                >
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >Organisation
                                                            Name</label
                                                        >
                                                        <div class="col-sm-9">
                                                            <input
                                                                v-model="
                                                                    org.organisation_name
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="first_name"
                                                                placeholder=""
                                                            />
                                                        </div>
                                                    </div>
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >Trading Name</label
                                                        >
                                                        <div class="col-sm-9">
                                                            <input
                                                                v-model="
                                                                    org.organisation_trading_name
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="trading_name"
                                                                placeholder=""
                                                            />
                                                        </div>
                                                    </div>
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >ABN</label
                                                        >
                                                        <div class="col-sm-9">
                                                            <input
                                                                v-model="
                                                                    org.organisation_abn
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="last_name"
                                                                placeholder=""
                                                                :disabled="
                                                                    !is_commercialoperator_admin
                                                                "
                                                            />
                                                        </div>
                                                    </div>
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >Email</label
                                                        >
                                                        <div class="col-sm-6">
                                                            <input
                                                                v-model="
                                                                    org.organisation_email
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="last_name"
                                                                placeholder=""
                                                            />
                                                        </div>
                                                    </div>
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <div class="row">
                                                            <div
                                                                class="col-sm-4"
                                                            >
                                                                <label
                                                                    class="control-label pull-right"
                                                                    for="Name"
                                                                    >Apply
                                                                    waiver for T
                                                                    Class
                                                                    application
                                                                    fee</label
                                                                >
                                                            </div>
                                                            <div
                                                                class="col-sm-1"
                                                            >
                                                                <label>
                                                                    <input
                                                                        ref="application_discount_yes"
                                                                        v-model="
                                                                            org.apply_application_discount
                                                                        "
                                                                        type="radio"
                                                                        :value="
                                                                            true
                                                                        "
                                                                    />Yes
                                                                </label>
                                                            </div>
                                                            <div
                                                                class="col-sm-1"
                                                            >
                                                                <label>
                                                                    <input
                                                                        v-model="
                                                                            org.apply_application_discount
                                                                        "
                                                                        type="radio"
                                                                        :value="
                                                                            false
                                                                        "
                                                                    />No
                                                                </label>
                                                            </div>
                                                            <div
                                                                class="col-sm-4"
                                                            >
                                                                <div
                                                                    v-show="
                                                                        org.apply_application_discount
                                                                    "
                                                                >
                                                                    <div
                                                                        class="col-sm-3"
                                                                    >
                                                                        <label
                                                                            class="control-label pull-left"
                                                                            for="Name"
                                                                            >Waiver</label
                                                                        >
                                                                    </div>
                                                                    <div
                                                                        class="col-sm-6 input-group"
                                                                    >
                                                                        <label
                                                                            class="input-group-addon"
                                                                            for="number"
                                                                            >$</label
                                                                        >
                                                                        <input
                                                                            v-model.number="
                                                                                org.application_discount
                                                                            "
                                                                            type="number"
                                                                            class="form-control"
                                                                            min="0"
                                                                            name="application_discount"
                                                                            @input="
                                                                                handleApplicationCurrencyInput
                                                                            "
                                                                        />
                                                                    </div>
                                                                    <div
                                                                        v-show="
                                                                            !validateApplicationDiscount()
                                                                        "
                                                                    >
                                                                        <p
                                                                            style="
                                                                                color: red;
                                                                            "
                                                                        >
                                                                            Waiver
                                                                            amount
                                                                            must
                                                                            be
                                                                            between
                                                                            $0 -
                                                                            $10,000
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <div class="row">
                                                            <div
                                                                class="col-sm-4"
                                                            >
                                                                <label
                                                                    class="control-label pull-right"
                                                                    for="Name"
                                                                    >Apply
                                                                    waiver for T
                                                                    Class
                                                                    licence
                                                                    fee</label
                                                                >
                                                            </div>
                                                            <div
                                                                class="col-sm-1"
                                                            >
                                                                <label>
                                                                    <input
                                                                        ref="licence_discount_yes"
                                                                        v-model="
                                                                            org.apply_licence_discount
                                                                        "
                                                                        type="radio"
                                                                        :value="
                                                                            true
                                                                        "
                                                                    />Yes
                                                                </label>
                                                            </div>
                                                            <div
                                                                class="col-sm-1"
                                                            >
                                                                <label>
                                                                    <input
                                                                        v-model="
                                                                            org.apply_licence_discount
                                                                        "
                                                                        type="radio"
                                                                        :value="
                                                                            false
                                                                        "
                                                                    />No
                                                                </label>
                                                            </div>
                                                            <div
                                                                class="col-sm-4"
                                                            >
                                                                <div
                                                                    v-show="
                                                                        org.apply_licence_discount
                                                                    "
                                                                >
                                                                    <div
                                                                        class="col-sm-3"
                                                                    >
                                                                        <label
                                                                            class="control-label pull-left"
                                                                            for="Name"
                                                                            >Waiver</label
                                                                        >
                                                                    </div>
                                                                    <div
                                                                        class="col-sm-6 input-group"
                                                                    >
                                                                        <label
                                                                            class="input-group-addon"
                                                                            for="number"
                                                                            >$</label
                                                                        >
                                                                        <input
                                                                            v-model.number="
                                                                                org.licence_discount
                                                                            "
                                                                            type="number"
                                                                            class="form-control"
                                                                            min="0"
                                                                            name="licence_discount"
                                                                            @input="
                                                                                handleLicenceCurrencyInput
                                                                            "
                                                                        />
                                                                    </div>
                                                                    <div
                                                                        v-show="
                                                                            !validateLicenceDiscount()
                                                                        "
                                                                    >
                                                                        <p
                                                                            style="
                                                                                color: red;
                                                                            "
                                                                        >
                                                                            Waiver
                                                                            amount
                                                                            must
                                                                            be
                                                                            between
                                                                            $0 -
                                                                            $10,000
                                                                        </p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <div class="row">
                                                            <div
                                                                class="col-sm-4"
                                                            >
                                                                <label
                                                                    class="control-label pull-right"
                                                                    for="Name"
                                                                    >Charge once
                                                                    per year -
                                                                    start of
                                                                    year<br />(Event
                                                                    Licence)</label
                                                                >
                                                            </div>
                                                            <div
                                                                class="col-sm-4"
                                                            >
                                                                <label>
                                                                    <input
                                                                        id="id_dt_clr"
                                                                        ref="charge_once_per_year"
                                                                        v-model="
                                                                            org.charge_once_per_year
                                                                        "
                                                                        type="text"
                                                                        class="form-control"
                                                                        placeholder="DD/MM"
                                                                        :title="
                                                                            charge_once_title()
                                                                        "
                                                                    />
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <div class="row">
                                                            <div
                                                                class="col-sm-4"
                                                            >
                                                                <label
                                                                    class="control-label pull-right"
                                                                    for="Name"
                                                                    >Maximum
                                                                    number of
                                                                    months
                                                                    ahead<br />(Event
                                                                    Licence)</label
                                                                >
                                                            </div>
                                                            <div
                                                                class="col-sm-2"
                                                            >
                                                                <label>
                                                                    <input
                                                                        ref="max_num_months_ahead"
                                                                        v-model="
                                                                            org.max_num_months_ahead
                                                                        "
                                                                        type="number"
                                                                        class="form-control"
                                                                        min="0"
                                                                        max="36"
                                                                        title="Max. months ahead for future Event application completion date"
                                                                    />
                                                                </label>
                                                            </div>
                                                        </div>
                                                    </div>

                                                    <div class="form-group row">
                                                        <div class="col-sm-12">
                                                            <button
                                                                v-if="
                                                                    !updatingDetails
                                                                "
                                                                class="btn btn-primary float-end"
                                                                :disabled="
                                                                    !can_update()
                                                                "
                                                                @click.prevent="
                                                                    updateDetails()
                                                                "
                                                            >
                                                                Update
                                                            </button>
                                                            <button
                                                                v-else
                                                                disabled
                                                                class="btn btn-primary float-end"
                                                            >
                                                                <i
                                                                    class="fa fa-spin fa-spinner"
                                                                ></i
                                                                >&nbsp;Updating
                                                            </button>
                                                        </div>
                                                    </div>
                                                </form>
                                            </FormSection>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <div class="panel panel-default">
                                            <FormSection
                                                :form-collapse="false"
                                                label="Address Details"
                                                index="address_details"
                                                subtitle=""
                                            >
                                                <form
                                                    class="form-horizontal"
                                                    action="index.html"
                                                    method="post"
                                                >
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >Street</label
                                                        >
                                                        <div class="col-sm-6">
                                                            <input
                                                                v-model="
                                                                    org
                                                                        .organisation_address
                                                                        .line1
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="street"
                                                                placeholder=""
                                                            />
                                                        </div>
                                                    </div>
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >Town/Suburb</label
                                                        >
                                                        <div class="col-sm-6">
                                                            <input
                                                                v-model="
                                                                    org
                                                                        .organisation_address
                                                                        .locality
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="surburb"
                                                                placeholder=""
                                                            />
                                                        </div>
                                                    </div>
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >State</label
                                                        >
                                                        <div class="col-sm-3">
                                                            <input
                                                                v-model="
                                                                    org
                                                                        .organisation_address
                                                                        .state
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="country"
                                                                placeholder=""
                                                            />
                                                        </div>
                                                        <label
                                                            for=""
                                                            class="col-sm-2 control-label"
                                                            >Postcode</label
                                                        >
                                                        <div class="col-sm-3">
                                                            <input
                                                                v-model="
                                                                    org
                                                                        .organisation_address
                                                                        .postcode
                                                                "
                                                                type="text"
                                                                class="form-control"
                                                                name="postcode"
                                                                placeholder=""
                                                            />
                                                        </div>
                                                    </div>
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <label
                                                            for=""
                                                            class="col-sm-3 control-label"
                                                            >Country</label
                                                        >
                                                        <div class="col-sm-4">
                                                            <select
                                                                v-model="
                                                                    org
                                                                        .organisation_address
                                                                        .country
                                                                "
                                                                class="form-control"
                                                                name="country"
                                                            >
                                                                <option
                                                                    v-for="c in countries"
                                                                    :key="
                                                                        c.code
                                                                    "
                                                                    :value="
                                                                        c.code
                                                                    "
                                                                >
                                                                    {{ c.name }}
                                                                </option>
                                                            </select>
                                                        </div>
                                                    </div>
                                                    <div class="form-group row">
                                                        <div class="col-sm-12">
                                                            <button
                                                                v-if="
                                                                    !updatingAddress
                                                                "
                                                                class="btn btn-primary float-end"
                                                                @click.prevent="
                                                                    updateAddress()
                                                                "
                                                            >
                                                                Update
                                                            </button>
                                                            <button
                                                                v-else
                                                                disabled
                                                                class="btn btn-primary float-end"
                                                            >
                                                                <i
                                                                    class="fa fa-spin fa-spinner"
                                                                ></i
                                                                >&nbsp;Updating
                                                            </button>
                                                        </div>
                                                    </div>
                                                </form>
                                            </FormSection>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <div class="panel panel-default">
                                            <FormSection
                                                :form-collapse="false"
                                                label="Contact Details"
                                                index="contact_details"
                                                subtitle=""
                                            >
                                                <form
                                                    class="form-horizontal"
                                                    action="index.html"
                                                    method="post"
                                                >
                                                    <div
                                                        class="form-group row mb-3"
                                                    >
                                                        <div class="col-sm-12">
                                                            <button
                                                                style="
                                                                    margin-bottom: 10px;
                                                                "
                                                                class="btn btn-primary float-end"
                                                                @click.prevent="
                                                                    addContact()
                                                                "
                                                            >
                                                                Add Contact
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <div class="form-group row">
                                                        <datatable
                                                            id="organisation_contacts_datatable"
                                                            ref="contacts_datatable"
                                                            :dt-options="
                                                                contacts_options
                                                            "
                                                            :dt-headers="
                                                                contacts_headers
                                                            "
                                                        />
                                                    </div>
                                                </form>
                                            </FormSection>
                                        </div>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col-sm-12">
                                        <div class="panel panel-default">
                                            <FormSection
                                                :form-collapse="false"
                                                label="Linked User Accounts"
                                                index="linked_user_accounts"
                                                subtitle="Manage the user accounts linked to the organisation"
                                            >
                                                <div class="row">
                                                    <div class="col-sm-12">
                                                        <div class="row">
                                                            <div
                                                                class="col-sm-12"
                                                            >
                                                                <h4>
                                                                    Persons
                                                                    linked to
                                                                    this
                                                                    organisation:
                                                                </h4>
                                                            </div>
                                                            <div
                                                                v-for="d in org.delegates"
                                                                :key="d.id"
                                                            >
                                                                <div
                                                                    v-if="
                                                                        d.is_admin
                                                                    "
                                                                    class="col-sm-6"
                                                                >
                                                                    <h4>
                                                                        {{
                                                                            d.name
                                                                        }}
                                                                        ({{
                                                                            d.email
                                                                        }}
                                                                        - Admin)
                                                                    </h4>
                                                                </div>
                                                                <div
                                                                    v-else
                                                                    class="col-sm-6"
                                                                >
                                                                    <h4>
                                                                        {{
                                                                            d.name
                                                                        }}
                                                                        ({{
                                                                            d.email
                                                                        }})
                                                                    </h4>
                                                                </div>
                                                            </div>
                                                            <div
                                                                class="col-sm-12 top-buffer-s mb-3"
                                                            >
                                                                <strong
                                                                    >Persons
                                                                    linked to
                                                                    the
                                                                    organisation
                                                                    are
                                                                    controlled
                                                                    by the
                                                                    organisation.
                                                                    The
                                                                    Department
                                                                    cannot
                                                                    manage this
                                                                    list of
                                                                    people.</strong
                                                                >
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>

                                                <form
                                                    v-if="org.pins"
                                                    class="form-horizontal"
                                                    action="index.html"
                                                    method="post"
                                                >
                                                    <div class="col-sm-6 row">
                                                        <div
                                                            class="form-group row mb-3"
                                                        >
                                                            <label
                                                                for=""
                                                                class="col-sm-6 control-label"
                                                            >
                                                                Organisation
                                                                User Pin Code
                                                                1:</label
                                                            >
                                                            <div
                                                                class="col-sm-6"
                                                            >
                                                                <label
                                                                    class="control-label"
                                                                    >{{
                                                                        org.pins
                                                                            .three
                                                                    }}</label
                                                                >
                                                            </div>
                                                        </div>
                                                        <div
                                                            class="form-group row mb-3"
                                                        >
                                                            <label
                                                                for=""
                                                                class="col-sm-6 control-label"
                                                                >Organisation
                                                                User Pin Code
                                                                2:</label
                                                            >
                                                            <div
                                                                class="col-sm-6"
                                                            >
                                                                <label
                                                                    class="control-label"
                                                                    >{{
                                                                        org.pins
                                                                            .four
                                                                    }}</label
                                                                >
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div class="col-sm-6 row">
                                                        <div
                                                            class="form-group row mb-3"
                                                        >
                                                            <label
                                                                for=""
                                                                class="col-sm-6 control-label"
                                                            >
                                                                Organisation
                                                                Administrator
                                                                Pin Code
                                                                1:</label
                                                            >
                                                            <div
                                                                class="col-sm-6"
                                                            >
                                                                <label
                                                                    class="control-label"
                                                                    >{{
                                                                        org.pins
                                                                            .one
                                                                    }}</label
                                                                >
                                                            </div>
                                                        </div>
                                                        <div
                                                            class="form-group row mb-3"
                                                        >
                                                            <label
                                                                for=""
                                                                class="col-sm-6 control-label"
                                                                >Organisation
                                                                Administrator
                                                                Pin Code
                                                                2:</label
                                                            >
                                                            <div
                                                                class="col-sm-6"
                                                            >
                                                                <label
                                                                    class="control-label"
                                                                    >{{
                                                                        org.pins
                                                                            .two
                                                                    }}</label
                                                                >
                                                            </div>
                                                        </div>
                                                    </div>
                                                </form>
                                                <div>
                                                    <datatable
                                                        id="organisation_contacts_datatable_ref"
                                                        ref="contacts_datatable_user"
                                                        v-model="
                                                            filterOrgContactStatus
                                                        "
                                                        :dt-options="
                                                            contacts_options_ref
                                                        "
                                                        :dt-headers="
                                                            contacts_headers_ref
                                                        "
                                                    />
                                                </div>
                                            </FormSection>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div
                                :id="oTab"
                                class="tab-pane fade"
                                role="tabpanel"
                                aria-labelledby="pills-other-tab"
                            >
                                <FormSection
                                    :form-collapse="false"
                                    label="Applications"
                                    index="applications"
                                >
                                    <ProposalDashTable
                                        ref="proposals_table"
                                        level="internal"
                                        :url="proposals_url"
                                    />
                                </FormSection>
                                <FormSection
                                    :form-collapse="false"
                                    label="Licences"
                                    index="approvals"
                                >
                                    <ApprovalDashTable
                                        ref="approvals_table"
                                        level="internal"
                                        :url="approvals_url"
                                    />
                                </FormSection>
                                <FormSection
                                    :form-collapse="false"
                                    label="Compliances"
                                    index="compliances"
                                >
                                    <ComplianceDashTable
                                        ref="compliances_table"
                                        level="internal"
                                        :url="compliances_url"
                                    />
                                </FormSection>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <AddContact ref="add_contact" :org_id="org.id" />
        <AddCommLog
            id="org_comms1"
            ref="add_comm_org"
            :url="comms_add_url"
            :action="user_action"
            @refreshActionFromResponse="refreshActionFromResponse"
        />
    </div>
</template>

<script>
import { api_endpoints, helpers } from '@/utils/hooks';
import datatable from '@vue-utils/datatable.vue';
import FormSection from '@/components/forms/section_toggle.vue';
import AddContact from '@common-utils/add_contact.vue';
import ProposalDashTable from '@common-utils/proposals_dashboard.vue';
import ApprovalDashTable from '@common-utils/approvals_dashboard.vue';
import ComplianceDashTable from '@common-utils/compliances_dashboard.vue';
import CommsLogs from '@common-utils/comms_logs.vue';
import utils from '../utils';
import AddCommLog from '@common-utils/add_comm_log_org.vue';
export default {
    // eslint-disable-next-line vue/multi-word-component-names
    name: 'Organisation',
    components: {
        datatable,
        FormSection,
        ProposalDashTable,
        ApprovalDashTable,
        ComplianceDashTable,
        AddContact,
        CommsLogs,
        AddCommLog,
    },
    beforeRouteEnter: function (to, from, next) {
        let initialisers = [
            utils.fetchCountries(),
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchProfile(),
        ];
        Promise.all(initialisers).then((data) => {
            next((vm) => {
                vm.countries = data[0];
                vm.org = data[1];
                vm.profile = data[2];
                vm.org.organisation_address =
                    vm.org.organisation_address != null
                        ? vm.org.organisation_address
                        : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
                vm.is_commercialoperator_admin =
                    vm.profile.is_commercialoperator_admin;
                vm.is_org_access_member = vm.profile.is_org_access_member;
            });
        });
    },
    beforeRouteUpdate: function (to, from, next) {
        let initialisers = [
            utils.fetchOrganisation(to.params.org_id),
            utils.fetchProfile(),
        ];
        Promise.all(initialisers).then((data) => {
            next((vm) => {
                vm.org = data[0];
                vm.profile = data[1];
                vm.is_commercialoperator_admin =
                    vm.profile.is_commercialoperator_admin;
                vm.is_org_access_member = vm.profile.is_org_access_member;
                vm.org.organisation_address =
                    vm.org.organisation_address != null
                        ? vm.org.organisation_address
                        : {};
                vm.org.pins = vm.org.pins != null ? vm.org.pins : {};
            });
        });
    },
    data() {
        let vm = this;
        return {
            adBody: 'adBody' + vm._uid,
            aBody: 'aBody' + vm._uid,
            pdBody: 'pdBody' + vm._uid,
            pBody: 'pBody' + vm._uid,
            cdBody: 'cdBody' + vm._uid,
            cBody: 'cBody' + vm._uid,
            oBody: 'oBody' + vm._uid,
            dTab: 'dTab' + vm._uid,
            oTab: 'oTab' + vm._uid,
            org: {
                organisation_address: {},
            },
            loading: [],
            countries: [],
            updatingDetails: false,
            updatingAddress: false,
            updatingContact: false,
            empty_list: '/api/empty_list',
            logsTable: null,
            prev_licence_discount: null,
            prev_application_discount: null,
            is_commercialoperator_admin: false,
            is_org_access_member: false,
            contact_user: {
                first_name: null,
                last_name: null,
                email: null,
                mobile_number: null,
                phone_number: null,
            },
            profile: {},
            user_action: 'unlink',
            DATE_TIME_FORMAT: 'DD/MM/YYYY HH:mm:ss',
            activate_tables: false,
            comms_url: helpers.add_endpoint_json(
                api_endpoints.organisations,
                vm.$route.params.org_id + '/comms_log'
            ),
            logs_url: helpers.add_endpoint_json(
                api_endpoints.organisations,
                vm.$route.params.org_id + '/action_log'
            ),
            comms_add_url: helpers.add_endpoint_json(
                api_endpoints.organisations,
                vm.$route.params.org_id + '/add_comms_log'
            ),

            contacts_headers: [
                'Name',
                'Phone',
                'Mobile',
                'Fax',
                'Email',
                'Action',
            ],

            proposals_url:
                api_endpoints.proposals_paginated_external +
                '&org_id=' +
                vm.$route.params.org_id,
            approvals_url:
                api_endpoints.approvals_paginated_external +
                '&org_id=' +
                vm.$route.params.org_id,
            compliances_url:
                api_endpoints.compliances_paginated_external +
                '&org_id=' +
                vm.$route.params.org_id,

            contacts_options: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/contacts'
                    ),
                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            if (full.is_admin) {
                                return (
                                    full.first_name +
                                    ' ' +
                                    full.last_name +
                                    ' (Admin)'
                                );
                            } else {
                                return full.first_name + ' ' + full.last_name;
                            }
                        },
                    },
                    { data: 'phone_number' },
                    { data: 'mobile_number' },
                    { data: 'fax_number' },
                    { data: 'email' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            let name = full.first_name + ' ' + full.last_name;
                            if (full.user_status == 'ContactForm') {
                                // can delete contacts that were added via the manage.vue 'Contact Details' form
                                links += `<a data-email='${full.email}' data-name='${name}' data-id='${full.id}' class="remove-contact">Remove</a><br/>`;
                            }
                            links += `<a data-email-edit='${full.email}' data-name-edit='${name}' data-edit-id='${full.id}' class="edit-contact">Edit</a><br/>`;
                            return links;
                        },
                    },
                ],
                processing: true,
            },

            contacts_headers_ref: ['Name', 'Role', 'Email', 'Status', 'Action'],
            contacts_options_ref: {
                language: {
                    processing: "<i class='fa fa-4x fa-spinner fa-spin'></i>",
                },
                responsive: true,
                ajax: {
                    url: helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.$route.params.org_id + '/contacts_exclude'
                    ),

                    dataSrc: '',
                },
                columns: [
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            return full.first_name + ' ' + full.last_name;
                        },
                    },
                    { data: 'user_role' },
                    { data: 'email' },
                    { data: 'user_status' },
                    {
                        data: 'id',
                        mRender: function (data, type, full) {
                            let links = '';
                            if (vm.is_commercialoperator_admin) {
                                if (full.user_status == 'Pending') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_contact">Accept</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="decline_contact">Decline</a><br/>`;
                                } else if (full.user_status == 'Suspended') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="reinstate_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Active') {
                                    links += `<a data-email='${full.email}' data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="unlink_contact">Unlink</a><br/>`;
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="suspend_contact">Suspend</a><br/>`;
                                    if (full.user_role == 'Organisation User') {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_admin_contact">Make Organisation Admin</a><br/>`;
                                    } else {
                                        links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="make_user_contact">Make Organisation User</a><br/>`;
                                    }
                                } else if (full.user_status == 'Unlinked') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="relink_contact">Reinstate</a><br/>`;
                                } else if (full.user_status == 'Declined') {
                                    links += `<a data-email='${full.email}'  data-firstname='${full.first_name}' data-lastname='${full.last_name}' data-id='${full.id}' data-mobile='${full.mobile_number}' data-phone='${full.phone_number}' class="accept_declined_contact">Accept (Previously Declined)</a><br/>`;
                                }
                            }
                            return links;
                        },
                    },
                ],
                processing: true,
            },
            // Note: Had to add this variable, it didn't exist. It is the model of the datatable component. What is it for?
            filterOrgContactStatus: null,
        };
    },
    computed: {
        isLoading: function () {
            return this.loading.length == 0;
        },
    },
    watch: {},
    mounted: function () {
        this.personal_form = document.forms.personal_form;
        this.eventListeners();
    },
    methods: {
        charge_once_title: function () {
            let vm = this;
            let ret = '';
            if (vm.org.last_event_application_fee_date) {
                ret =
                    'Charge once per year start: ' +
                    vm.org.last_event_application_fee_date +
                    '. ' +
                    'Next Event application fee to be charged after: ' +
                    moment(vm.org.last_event_application_fee_date, 'DD/MM/YYYY')
                        .add(12, 'months')
                        .format('DD/MM/YYYY');
            } else {
                ret =
                    'Next Event application will be charged (first in current year). ';
            }
            return ret;
        },
        handleApplicationCurrencyInput(e) {
            // allow max 2dp
            let vm = this;
            let stringValue = e.target.value.toString();
            let regex = /^\d*(\.\d{1,2})?$/;
            if (!stringValue.match(regex) && vm.org.licence_discount !== '') {
                vm.org.application_discount = vm.prev_application_discount;
            }
            vm.prev_application_discount = vm.org.application_discount;
        },
        handleLicenceCurrencyInput(e) {
            // allow max 2dp
            let vm = this;
            let stringValue = e.target.value.toString();
            let regex = /^\d*(\.\d{1,2})?$/;
            if (!stringValue.match(regex) && vm.org.licence_discount !== '') {
                vm.org.licence_discount = vm.prev_licence_discount;
            }
            vm.prev_licence_discount = vm.org.licence_discount;
        },
        validateApplicationDiscount: function () {
            if (
                this.org.application_discount < 0 ||
                this.org.application_discount > 10000
            ) {
                return false;
            }
            return true;
        },
        validateLicenceDiscount: function () {
            if (
                this.org.licence_discount < 0 ||
                this.org.licence_discount > 10000
            ) {
                return false;
            }
            return true;
        },
        can_update: function () {
            // can update the Organisation section
            if (
                this.validateApplicationDiscount() &&
                this.validateLicenceDiscount()
            ) {
                return true;
            }
            return false;
        },

        addContact: function () {
            this.$refs.add_contact.isModalOpen = true;
        },
        editContact: function (_id) {
            let vm = this;
            vm.$http
                .get(
                    helpers.add_endpoint_json(
                        api_endpoints.organisation_contacts,
                        _id
                    )
                )
                .then((response) => {
                    this.$refs.add_contact.contact = response.body;
                    this.addContact();
                })
                .then(
                    () => {
                        this.$refs.contacts_datatable.vmDataTable.ajax.reload();
                    },
                    (error) => {
                        console.log(error);
                    }
                );
        },
        refreshDatatable: function () {
            this.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        refreshActionFromResponse: function (action) {
            let vm = this;
            if (action && this.action === action) {
                if (action == 'unlink') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/unlink_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Unlink',
                                    text:
                                        'You have successfully unlinked ' +
                                        name +
                                        '.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                if (error.status == 500) {
                                    swal.fire({
                                        title: 'Unlink',
                                        text: 'Last Organisation Admin can not be unlinked.',
                                        icon: 'error',
                                    });
                                } else {
                                    swal.fire({
                                        title: 'Unlink',
                                        text:
                                            'There was an error unlinking ' +
                                            error.body +
                                            '.',
                                        icon: 'error',
                                    });
                                }
                            }
                        );
                } else if (action == 'relink') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/relink_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Relink User',
                                    text:
                                        'You have successfully relinked ' +
                                        name +
                                        '.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                swal.fire({
                                    title: 'Relink User',
                                    text:
                                        'There was an error relinking ' +
                                        error.body +
                                        '.',
                                    icon: 'error',
                                });
                            }
                        );
                } else if (action == 'suspend') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/suspend_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Suspend User',
                                    text:
                                        'You have successfully suspended ' +
                                        name +
                                        ' as a User.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                swal.fire({
                                    title: 'Suspend User',
                                    text:
                                        'There was an error suspending ' +
                                        error.body +
                                        ' as a User.',
                                    icon: 'error',
                                });
                            }
                        );
                } else if (action == 'reinstate') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/reinstate_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Reinstate User',
                                    text:
                                        'You have successfully reinstated ' +
                                        name +
                                        '.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                swal.fire({
                                    title: 'Reinstate User',
                                    text:
                                        'There was an error reinstating ' +
                                        error.body +
                                        '.',
                                    icon: 'error',
                                });
                            }
                        );
                } else if (action == 'make_admin_contact') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/make_admin_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Organisation Admin',
                                    text:
                                        'You have successfully made ' +
                                        name +
                                        ' an Organisation Admin.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                swal.fire({
                                    title: 'Organisation Admin',
                                    text:
                                        'There was an error making ' +
                                        error.body +
                                        ' an Organisation Admin.',
                                    icon: 'error',
                                });
                            }
                        );
                } else if (action == 'make_user_contact') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/make_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Organisation User',
                                    text:
                                        'You have successfully made ' +
                                        name +
                                        ' an Organisation User.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                console.log(error);
                                var text = helpers.apiVueResourceError(error);
                                swal.fire({
                                    title: 'Company Admin',
                                    text:
                                        'There was an error making ' +
                                        error.body +
                                        ' an Organisation User.' +
                                        text,
                                    icon: 'error',
                                });
                            }
                        );
                } else if (action == 'accept') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/accept_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Contact Accept',
                                    text:
                                        'You have successfully accepted ' +
                                        name +
                                        '.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                swal.fire({
                                    title: 'Contact Accept',
                                    text:
                                        'There was an error accepting ' +
                                        error.body +
                                        '.',
                                    icon: 'error',
                                });
                            }
                        );
                } else if (action == 'decline') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/decline_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Contact Decline',
                                    text:
                                        'You have successfully declined ' +
                                        name +
                                        '.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                swal.fire({
                                    title: 'Contact Decline',
                                    text:
                                        'There was an error declining ' +
                                        error.body +
                                        '.',
                                    icon: 'error',
                                });
                            }
                        );
                } else if (action == 'accept_declined') {
                    vm.$http
                        .post(
                            helpers.add_endpoint_json(
                                api_endpoints.organisations,
                                vm.org.id + '/accept_declined_user'
                            ),
                            JSON.stringify(vm.contact_user),
                            {
                                emulateJSON: true,
                            }
                        )
                        .then(
                            () => {
                                // Note: This block is missing a response to retrieve the name from
                                swal.fire({
                                    title: 'Contact Accept (Previously Declined)',
                                    text:
                                        'You have successfully accepted ' +
                                        name +
                                        '.',
                                    icon: 'success',
                                    confirmButtonText: 'OK',
                                }).then(
                                    () => {
                                        vm.$refs.contacts_datatable_user.vmDataTable.ajax.reload();
                                    },
                                    () => {}
                                );
                            },
                            (error) => {
                                // Note: The alert text seems to indicate to display the user name, but the name is not retrieved from the error response
                                swal.fire({
                                    title: 'Contact Accept (Previously Declined)',
                                    text:
                                        'There was an error accepting ' +
                                        error.body +
                                        '.',
                                    icon: 'error',
                                });
                            }
                        );
                }
            }
        },
        eventListeners: function () {
            let vm = this;
            vm.$refs.contacts_datatable.vmDataTable.on(
                'click',
                '.remove-contact',
                (e) => {
                    e.preventDefault();

                    let name = $(e.target).data('name');
                    let email = $(e.target).data('email');
                    let id = $(e.target).data('id');
                    swal.fire({
                        title: 'Delete Contact',
                        text:
                            'Are you sure you want to remove ' +
                            name +
                            '(' +
                            email +
                            ') as a contact  ?',
                        icon: 'error',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        () => {
                            vm.deleteContact(id);
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable.vmDataTable.on(
                'click',
                '.edit-contact',
                (e) => {
                    e.preventDefault();
                    let id = $(e.target).attr('data-edit-id');
                    vm.editContact(id);
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.unlink_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Unlink',
                        text:
                            'Are you sure you want to unlink ' +
                            name +
                            ' (' +
                            email +
                            ')?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        async (result) => {
                            if (result) {
                                this.action = 'unlink';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.reinstate_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Reinstate User',
                        text:
                            'Are you sure you want to Reinstate  ' +
                            name +
                            ' (' +
                            email +
                            ')?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'reinstate';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.relink_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Relink User',
                        text:
                            'Are you sure you want to Relink  ' +
                            name +
                            ' (' +
                            email +
                            ')?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'relink';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.suspend_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Suspend User',
                        text:
                            'Are you sure you want to Suspend  ' +
                            name +
                            ' (' +
                            email +
                            ')?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'suspend';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.make_admin_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Organisation Admin',
                        text:
                            'Are you sure you want to make ' +
                            name +
                            ' (' +
                            email +
                            ') an Organisation Admin?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'make_admin_contact';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.make_user_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Organisation User',
                        text:
                            'Are you sure you want to make ' +
                            name +
                            ' (' +
                            email +
                            ') an Organisation User?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'make_user_contact';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.accept_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Contact Accept',
                        text:
                            'Are you sure you want to accept contact request ' +
                            name +
                            ' (' +
                            email +
                            ')?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'accept';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.decline_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Contact Decline',
                        text:
                            'Are you sure you want to decline the contact request for ' +
                            name +
                            ' (' +
                            email +
                            ')?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'decline';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );

            vm.$refs.contacts_datatable_user.vmDataTable.on(
                'click',
                '.accept_declined_contact',
                (e) => {
                    e.preventDefault();
                    let firstname = $(e.target).data('firstname');
                    let lastname = $(e.target).data('lastname');
                    let name = firstname + ' ' + lastname;
                    let email = $(e.target).data('email');
                    let mobile = $(e.target).data('mobile');
                    let phone = $(e.target).data('phone');
                    vm.contact_user.first_name = firstname;
                    vm.contact_user.last_name = lastname;
                    vm.contact_user.email = email;
                    vm.contact_user.mobile_number = mobile;
                    vm.contact_user.phone_number = phone;
                    swal.fire({
                        title: 'Contact Accept (Previously Declined)',
                        text:
                            'Are you sure you want to accept the previously declined contact request for ' +
                            name +
                            ' (' +
                            email +
                            ')?',
                        showCancelButton: true,
                        confirmButtonText: 'Accept',
                    }).then(
                        (result) => {
                            if (result) {
                                this.action = 'accept_declined';
                                this.$refs.add_comm_org.localAction =
                                    this.action;
                                this.addComm();
                            }
                        },
                        () => {}
                    );
                }
            );
            // Fix the table responsiveness when tab is shown
            $('a[href="#' + vm.oTab + '"]').on('shown.bs.tab', function () {
                vm.$refs.proposals_table.$refs.proposal_datatable.vmDataTable.columns
                    .adjust()
                    .responsive.recalc();
                vm.$refs.approvals_table.$refs.proposal_datatable.vmDataTable.columns
                    .adjust()
                    .responsive.recalc();
                vm.$refs.compliances_table.$refs.proposal_datatable.vmDataTable.columns
                    .adjust()
                    .responsive.recalc();
            });
        },
        addComm() {
            this.$refs.add_comm_org.isModalOpen = true;
        },
        updateDetails: function () {
            let vm = this;
            vm.updatingDetails = true;
            vm.$http
                .post(
                    helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.org.id + '/update_details'
                    ),
                    JSON.stringify(vm.org),
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    (response) => {
                        vm.updatingDetails = false;
                        vm.org = response.body;
                        if (vm.org.organisation_address == null) {
                            vm.org.organisation_address = {};
                        }
                        swal.fire({
                            title: 'Saved',
                            text: 'Organisation details have been saved',
                            icon: 'success',
                        });
                    },
                    (error) => {
                        console.log('INTERNAL: ', error);
                        var text = helpers.apiVueResourceError(error);
                        if (typeof text == 'object') {
                            // eslint-disable-next-line no-prototype-builtins
                            if (text.hasOwnProperty('email')) {
                                text = text.email[0];
                            }
                        }
                        swal.fire({
                            title: 'Error',
                            html:
                                'Organisation details cannot be saved because of the following error: ' +
                                vm.parseErrorMessages(error),
                            icon: 'error',
                        });
                        vm.updatingDetails = false;
                    }
                );
        },
        addedContact: function () {
            let vm = this;
            swal.fire({
                title: 'Added',
                text: 'The contact has been successfully added.',
                icon: 'success',
            });
            vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
        },
        deleteContact: function (id) {
            let vm = this;

            vm.$http
                .delete(
                    helpers.add_endpoint_json(
                        api_endpoints.organisation_contacts,
                        id
                    ),
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    () => {
                        swal.fire({
                            title: 'Contact Deleted',
                            text: 'The contact has been successfully deleted.',
                            icon: 'success',
                        });
                        vm.$refs.contacts_datatable.vmDataTable.ajax.reload();
                    },
                    (error) => {
                        console.log(error);
                        swal.fire({
                            title: 'Contact Deleted',
                            text:
                                'The contact could not be deleted because of the following error : [' +
                                error.body +
                                ']',
                            icon: 'error',
                        });
                    }
                );
        },
        updateAddress: function () {
            let vm = this;
            vm.updatingAddress = true;
            vm.$http
                .post(
                    helpers.add_endpoint_json(
                        api_endpoints.organisations,
                        vm.org.id + '/update_address'
                    ),
                    JSON.stringify(vm.org.organisation_address),
                    {
                        emulateJSON: true,
                    }
                )
                .then(
                    (response) => {
                        vm.updatingAddress = false;
                        vm.org = response.body;
                        swal.fire({
                            title: 'Saved',
                            text: 'Address details have been saved',
                            icon: 'success',
                        });
                        if (vm.org.organisation_address == null) {
                            vm.org.organisation_address = {};
                        }
                    },
                    (error) => {
                        console.log(error);
                        swal.fire({
                            title: 'Error',
                            text:
                                'Address details cannot be saved because of the following error: ' +
                                (error.body.message || error.body.detail),
                            icon: 'error',
                        });
                        vm.updatingAddress = false;
                    }
                );
        },
        parseErrorMessages(error) {
            let error_msg = '<br/>';
            for (let key in error.body) {
                error_msg += key + ': ' + error.body[key] + '<br/>';
            }
            return error_msg;
        },
    },
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.top-buffer-s {
    margin-top: 10px;
}
.actionBtn {
    cursor: pointer;
}
.hidePopover {
    display: none;
}

.input-group {
    display: table;
    white-space: nowrap;
    vertical-align: top;
    width: 75%;
}
.input-group .form-control {
    display: table-cell;
    vertical-align: top;
    width: 75%;
}
.input-group .input-group-addon {
    display: table-cell;
    width: 1%;
    vertical-align: top;
    background: #2f353e;
    color: #fff;
    font-size: 1.15rem;
    line-height: 19px;
    padding-left: 10px;
    padding-right: 10px;
}
</style>
