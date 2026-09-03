// Copyright (c) 2026, OSDuo and contributors
// For license information, please see license.txt

frappe.pages["analytics"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Analytics Dashboard"),
		single_column: true,
	});

	page.add_field({
		fieldname: "business",
		label: __("Business"),
		fieldtype: "Link",
		options: "Business",
		reqd: 1,
		change: function () {
			load_analytics(page);
		},
	});

	page.add_field({
		fieldname: "days",
		label: __("Period"),
		fieldtype: "Select",
		options: "7\n15\n30\n90\n365",
		default: "30",
		change: function () {
			load_analytics(page);
		},
	});

	page.fields_dict.business.$wrapper.css("min-width", "300px");
	page.fields_dict.days.$wrapper.css("min-width", "120px");

	// Main container
	page.main.append(`<div id="analytics-loading" class="text-muted" style="padding:2rem;text-align:center;">
		${__("Loading analytics...")}
	</div>`);

	page.main.append(`<div id="analytics-content" style="display:none;"></div>`);

	load_business_list(page);
};

function load_business_list(page) {
	frappe.call({
		method: "osduo_business_connect.pages.analytics.get_business_list",
		callback: function (r) {
			if (r.message && r.message.length) {
				page.fields_dict.business.$input.val(r.message[0].name).trigger("change");
			}
		},
	});
}

function load_analytics(page) {
	var business = page.fields_dict.business.$input.val();
	var days = page.fields_dict.days.get_value();
	if (!business) return;

	$("#analytics-loading").show();
	$("#analytics-content").hide();

	frappe.call({
		method: "osduo_business_connect.pages.analytics.get_analytics",
		args: { business: business, days: days },
		callback: function (r) {
			$("#analytics-loading").hide();
			$("#analytics-content").show();
			if (r.message) render_analytics(page, r.message);
		},
	});
}

function render_analytics(page, data) {
	var eng = data.engagement;
	var enq = data.enquiry_stats;
	var summary = data.summary;

	var html = `
		<div class="row" style="margin-bottom:1.5rem;">
			<div class="col-sm-3">
				<div class="frappe-card" style="padding:1rem;text-align:center;">
					<div style="font-size:2rem;font-weight:700;color:var(--primary);">${eng.total_events || 0}</div>
					<div style="font-size:0.8rem;color:#888;">${__("Link Visits")}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card" style="padding:1rem;text-align:center;">
					<div style="font-size:2rem;font-weight:700;color:#2490ef;">${eng.qr_scans || 0}</div>
					<div style="font-size:0.8rem;color:#888;">${__("QR Scans")}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card" style="padding:1rem;text-align:center;">
					<div style="font-size:2rem;font-weight:700;color:#28a745;">${summary.total_cards || 0}</div>
					<div style="font-size:0.8rem;color:#888;">${__("Cards")}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card" style="padding:1rem;text-align:center;">
					<div style="font-size:2rem;font-weight:700;color:#f5a623;">${summary.total_products || 0}</div>
					<div style="font-size:0.8rem;color:#888;">${__("Products")}</div>
				</div>
			</div>
		</div>

		<div class="row" style="margin-bottom:1.5rem;">
			<div class="col-sm-8">
				<div class="frappe-card" style="padding:1.2rem;">
					<h5 style="margin-bottom:1rem;">${__("Visits by Day")}</h5>
					<div id="chart-visits-by-day" style="height:220px;"></div>
				</div>
			</div>
			<div class="col-sm-4">
				<div class="frappe-card" style="padding:1.2rem;">
					<h5 style="margin-bottom:1rem;">${__("Events by Type")}</h5>
					<div id="events-by-type-list"></div>
				</div>
			</div>
		</div>

		<div class="row" style="margin-bottom:1.5rem;">
			<div class="col-sm-6">
				<div class="frappe-card" style="padding:1.2rem;">
					<h5 style="margin-bottom:1rem;">${__("Top Cards")}</h5>
					<div id="top-cards-list"></div>
				</div>
			</div>
			<div class="col-sm-6">
				<div class="frappe-card" style="padding:1.2rem;">
					<h5 style="margin-bottom:1rem;">${__("Enquiry Pipeline")}</h5>
					<div id="enquiry-pipeline"></div>
				</div>
			</div>
		</div>

		<div class="row">
			<div class="col-sm-12">
				<div class="frappe-card" style="padding:1.2rem;">
					<h5 style="margin-bottom:1rem;">${__("Recent Activity")}</h5>
					<div id="recent-activity-list"></div>
				</div>
			</div>
		</div>
	`;

	page.main.find("#analytics-content").html(html);

	render_bar_chart("chart-visits-by-day", eng.events_by_day || []);
	render_events_by_type("events-by-type-list", eng.events_by_type || {});
	render_top_cards("top-cards-list", data.top_cards || []);
	render_enquiry_pipeline("enquiry-pipeline", enq);
	render_recent_activity("recent-activity-list", eng.recent_events || []);
}

function render_bar_chart(container_id, data) {
	var container = document.getElementById(container_id);
	if (!data.length) {
		container.innerHTML = `<p style="color:#888;text-align:center;padding:2rem;">${__("No data for this period")}</p>`;
		return;
	}
	var max = Math.max.apply(
		null,
		data.map(function (d) {
			return d.count;
		})
	);
	var html =
		'<div style="display:flex;align-items:flex-end;gap:3px;height:180px;padding-top:10px;">';
	data.forEach(function (d) {
		var h = max > 0 ? (d.count / max) * 160 : 0;
		html += '<div style="flex:1;display:flex;flex-direction:column;align-items:center;">';
		html +=
			'<div style="font-size:0.65rem;color:#666;margin-bottom:2px;">' + d.count + "</div>";
		html +=
			'<div style="width:100%;background:var(--primary);border-radius:3px 3px 0 0;height:' +
			h +
			'px;min-height:2px;" title="' +
			d.date +
			": " +
			d.count +
			'"></div>';
		html +=
			'<div style="font-size:0.55rem;color:#888;margin-top:3px;writing-mode:vertical-rl;transform:rotate(180deg);max-height:50px;overflow:hidden;">' +
			d.date.slice(5) +
			"</div>";
		html += "</div>";
	});
	html += "</div>";
	container.innerHTML = html;
}

function render_events_by_type(container_id, data) {
	var container = document.getElementById(container_id);
	var keys = Object.keys(data);
	if (!keys.length) {
		container.innerHTML = `<p style="color:#888;">${__("No events recorded")}</p>`;
		return;
	}
	var total = keys.reduce(function (s, k) {
		return s + data[k];
	}, 0);
	var html =
		'<table class="table table-bordered" style="font-size:0.8rem;"><thead><tr><th>' +
		__("Event") +
		'</th><th style="text-align:right">' +
		__("Count") +
		'</th><th style="text-align:right">' +
		__("Share") +
		"</th></tr></thead><tbody>";
	keys
		.sort(function (a, b) {
			return data[b] - data[a];
		})
		.forEach(function (k) {
			var pct = total > 0 ? ((data[k] / total) * 100).toFixed(1) : 0;
			html +=
				"<tr><td>" +
				k.replace(/_/g, " ") +
				'</td><td style="text-align:right">' +
				data[k] +
				'</td><td style="text-align:right">' +
				pct +
				"%</td></tr>";
		});
	html += "</tbody></table>";
	container.innerHTML = html;
}

function render_top_cards(container_id, data) {
	var container = document.getElementById(container_id);
	if (!data.length) {
		container.innerHTML = `<p style="color:#888;">${__("No card views yet")}</p>`;
		return;
	}
	var html =
		'<table class="table table-bordered" style="font-size:0.8rem;"><thead><tr><th>' +
		__("Card") +
		'</th><th style="text-align:right">' +
		__("Views") +
		"</th></tr></thead><tbody>";
	data.forEach(function (d) {
		html +=
			"<tr><td>" +
			(d.card || "\u2014") +
			'</td><td style="text-align:right">' +
			d.views +
			"</td></tr>";
	});
	html += "</tbody></table>";
	container.innerHTML = html;
}

function render_enquiry_pipeline(container_id, data) {
	var container = document.getElementById(container_id);
	var items = [
		{ label: __("New"), value: data.new || 0, color: "#2490ef" },
		{ label: __("Synced"), value: data.synced || 0, color: "#f5a623" },
		{ label: __("Converted"), value: data.converted || 0, color: "#28a745" },
	];
	var html = '<div style="display:flex;gap:1rem;">';
	items.forEach(function (item) {
		html +=
			'<div style="flex:1;text-align:center;padding:0.8rem;border:1px solid #e2e8f0;border-radius:6px;">';
		html +=
			'<div style="font-size:1.4rem;font-weight:700;color:' +
			item.color +
			";\">" +
			item.value +
			"</div>";
		html += '<div style="font-size:0.75rem;color:#666;">' + item.label + "</div>";
		html += "</div>";
	});
	html += "</div>";
	container.innerHTML = html;
}

function render_recent_activity(container_id, data) {
	var container = document.getElementById(container_id);
	if (!data.length) {
		container.innerHTML = `<p style="color:#888;">${__("No recent activity")}</p>`;
		return;
	}
	var html =
		'<table class="table table-bordered" style="font-size:0.8rem;"><thead><tr><th>' +
		__("Time") +
		'</th><th>' +
		__("Event") +
		'</th><th>' +
		__("Page") +
		'</th><th>' +
		__("Device") +
		"</th></tr></thead><tbody>";
	data.forEach(function (d) {
		var page_name = d.card || d.product || d.service || "\u2014";
		html +=
			"<tr><td>" +
			frappe.datetime.str_to_user(d.event_time) +
			"</td><td>" +
			(d.event_type || "").replace(/_/g, " ") +
			"</td><td>" +
			page_name +
			"</td><td>" +
			(d.device_type || "Unknown") +
			"</td></tr>";
	});
	html += "</tbody></table>";
	container.innerHTML = html;
}
