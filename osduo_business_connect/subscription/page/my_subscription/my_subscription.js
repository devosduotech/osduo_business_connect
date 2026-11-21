// My Subscription — read-only plan, usage and add-on summary.
// No payment, checkout or invoice UI lives here; billing is handled at Aasriva.

frappe.pages["my-subscription"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("My Subscription"),
		single_column: true,
	});

	page.set_primary_action(__("Request add-on"), () => {
		frappe.new_doc("Add-on Order");
	});

	const body = $(wrapper).find(".page-content");
	body.html(`<div class="text-muted">${__("Loading subscription…")}</div>`);

	frappe.call({
		method: "osduo_business_connect.subscription.subscription_page.get_my_subscription",
		callback(r) {
			body.html(render(r.message || {}));
		},
		error() {
			body.html(`<div class="alert alert-danger">${__("Could not load subscription details.")}</div>`);
		},
	});
};

function esc(value) {
	return $("<div>").text(value == null ? "—" : String(value)).html();
}

function money(value) {
	return "₹" + Number(value || 0).toLocaleString("en-IN");
}

function render(data) {
	const seats = data.seats || {};
	const businesses = data.businesses || {};
	const domains = data.domains || {};
	const enabled = new Set(
		(data.features || []).filter((f) => f.enabled).map((f) => f.key)
	);

	const chips = (data.features || [])
		.filter((f) => f.enabled)
		.map((f) => `<span class="badge badge-secondary">${esc(f.label)}</span>`)
		.join(" ");

	const rows = (domains.rows || [])
		.map(
			(row) => `<tr>
				<td>${esc(row.hostname)}</td>
				<td>${esc(row.mapping_type)}</td>
				<td>${row.mapping_type === "Included" ? "₹0" : money(row.price)}</td>
				<td>${esc(row.status)}</td>
				<td>${esc(row.expires_on)}</td>
			</tr>`
		)
		.join("");

	return `
		<div class="bc-subscription">
			<p class="text-muted">
				${esc(data.status)} · annual plan · renews ${esc(data.period_end)} ·
				billed through ${esc(data.billing_source)}
			</p>
			<div class="row">
				${kpi(__("Plan"), esc(data.plan), money(data.price_per_seat_per_year) + " / user / year")}
				${kpi(__("Billed seats"), `${seats.used} of ${seats.billed}`, __("minimum always billed"))}
				${kpi(__("Business profiles"), `${businesses.used} of ${businesses.cap}`, __("drafts count toward cap"))}
				${kpi(__("Custom domains"), domains.included ? `${domains.included} included` : "None included", money(domains.price) + " / year extra")}
			</div>
			<h4>${__("Seats &amp; usage")}</h4>
			${usage(__("Users / seats"), seats.used, seats.billed)}
			${usage(__("Business profiles"), businesses.used, businesses.cap)}
			<p class="text-muted">${__("Cancelled businesses (not counted):")} ${businesses.cancelled}</p>
			<h4>${__("Custom domains &amp; add-ons")}</h4>
			<table class="table table-bordered">
				<thead><tr><th>${__("Domain")}</th><th>${__("Type")}</th><th>${__("Price")}</th><th>${__("Status")}</th><th>${__("Expiry")}</th></tr></thead>
				<tbody>${rows || `<tr><td colspan="5" class="text-muted">${__("No domains yet")}</td></tr>`}</tbody>
			</table>
			<p class="text-muted">${__("Expiry follows the subscription period end. Adding a domain never changes printed QR / NFC URLs.")}</p>
			<h4>${__("Included in your plan")}</h4>
			<p>${chips || __("Core digital card features")}</p>
			<p class="text-muted">${__("External CRM apps:")} ${data.external_crm_enabled ? __("enabled") : __("disabled at instance creation")}</p>
			${data.upgrade_url ? `<a class="btn btn-primary" href="${esc(data.upgrade_url)}" target="_blank" rel="noopener">${__("View plans on Aasriva")}</a>` : ""}
			${enabled.has("advanced_admin") ? "" : `<p class="text-muted">${__("Advanced administration is available on Enterprise.")}</p>`}
		</div>`;
}

function kpi(label, value, sub) {
	return `<div class="col-sm-6 col-md-3">
		<div class="card"><div class="card-body">
			<div class="text-muted small">${label}</div>
			<div class="h4">${value}</div>
			<div class="text-muted small">${sub}</div>
		</div></div>
	</div>`;
}

function usage(label, used, total) {
	const pct = total > 0 ? Math.min(100, Math.round((used / total) * 100)) : 0;
	return `<div class="mb-3">
		<div><strong>${label}</strong>: ${used} / ${total}</div>
		<div class="progress"><div class="progress-bar" style="width:${pct}%"></div></div>
	</div>`;
}
