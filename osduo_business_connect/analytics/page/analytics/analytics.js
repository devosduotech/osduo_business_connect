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
				<div class="frappe-card" style="padding:1rem;text-align:center;border-left:4px solid #4f46e5;">
					<div style="font-size:2rem;font-weight:700;color:#4f46e5;">${eng.total_events || 0}</div>
					<div style="font-size:0.8rem;color:#666;">${__("Link Visits")}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card" style="padding:1rem;text-align:center;border-left:4px solid #0ea5e9;">
					<div style="font-size:2rem;font-weight:700;color:#0ea5e9;">${eng.qr_scans || 0}</div>
					<div style="font-size:0.8rem;color:#666;">${__("QR Scans")}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card" style="padding:1rem;text-align:center;border-left:4px solid #10b981;">
					<div style="font-size:2rem;font-weight:700;color:#10b981;">${summary.total_cards || 0}</div>
					<div style="font-size:0.8rem;color:#666;">${__("Cards")}</div>
				</div>
			</div>
			<div class="col-sm-3">
				<div class="frappe-card" style="padding:1rem;text-align:center;border-left:4px solid #f59e0b;">
					<div style="font-size:2rem;font-weight:700;color:#f59e0b;">${summary.total_products || 0}</div>
					<div style="font-size:0.8rem;color:#666;">${__("Products")}</div>
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

	var w = container.offsetWidth || 700;
	var h = 200;
	var pad = { top: 20, right: 20, bottom: 40, left: 40 };
	var chart_w = w - pad.left - pad.right;
	var chart_h = h - pad.top - pad.bottom;

	var max = Math.max.apply(
		null,
		data.map(function (d) {
			return d.count;
		})
	);
	if (max === 0) max = 1;

	var points = data.map(function (d, i) {
		var x = pad.left + (i / (data.length - 1 || 1)) * chart_w;
		var y = pad.top + chart_h - (d.count / max) * chart_h;
		return { x: x, y: y, date: d.date, count: d.count };
	});

	var path_d = points
		.map(function (p, i) {
			return (i === 0 ? "M" : "L") + p.x + "," + p.y;
		})
		.join(" ");

	var area_d =
		path_d +
		" L" +
		points[points.length - 1].x +
		"," +
		(pad.top + chart_h) +
		" L" +
		points[0].x +
		"," +
		(pad.top + chart_h) +
		" Z";

	var svg = `<svg width="${w}" height="${h}" style="display:block;">`;
	svg += `<defs>
		<linearGradient id="lineGrad" x1="0" y1="0" x2="0" y2="1">
			<stop offset="0%" stop-color="#4f46e5" stop-opacity="0.3"/>
			<stop offset="100%" stop-color="#4f46e5" stop-opacity="0.02"/>
		</linearGradient>
	</defs>`;

	// Grid lines
	for (var g = 0; g <= 4; g++) {
		var gy = pad.top + (chart_h / 4) * g;
		var gval = Math.round(max - (max / 4) * g);
		svg += `<line x1="${pad.left}" y1="${gy}" x2="${w - pad.right}" y2="${gy}" stroke="#e5e7eb" stroke-width="1"/>`;
		svg += `<text x="${pad.left - 6}" y="${gy + 4}" text-anchor="end" fill="#9ca3af" font-size="10">${gval}</text>`;
	}

	// Area fill
	svg += `<path d="${area_d}" fill="url(#lineGrad)"/>`;

	// Line
	svg += `<path d="${path_d}" fill="none" stroke="#4f46e5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>`;

	// Dots
	points.forEach(function (p) {
		svg += `<circle cx="${p.x}" cy="${p.y}" r="3.5" fill="#4f46e5" stroke="#fff" stroke-width="2"/>`;
	});

	// X-axis labels (show every Nth)
	var label_every = Math.max(1, Math.floor(data.length / 8));
	points.forEach(function (p, i) {
		if (i % label_every === 0 || i === points.length - 1) {
			svg += `<text x="${p.x}" y="${h - 8}" text-anchor="middle" fill="#9ca3af" font-size="9">${p.date.slice(5)}</text>`;
		}
	});

	svg += "</svg>";
	container.innerHTML = svg;
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
				k.replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); }) +
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
		__("Member") +
		'</th><th style="text-align:right">' +
		__("Views") +
		"</th></tr></thead><tbody>";
	data.forEach(function (d) {
		html +=
			"<tr><td>" +
			(d.member_name || d.card || "\u2014") +
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
		var page_name = d.person_name || d.card || d.product || d.service || "\u2014";
		html +=
			"<tr><td>" +
			frappe.datetime.str_to_user(d.event_time) +
			"</td><td>" +
			(d.event_type || "").replace(/_/g, " ").replace(/\b\w/g, function (c) { return c.toUpperCase(); }) +
			"</td><td>" +
			page_name +
			"</td><td>" +
			(d.device_type || "Unknown") +
			"</td></tr>";
	});
	html += "</tbody></table>";
	container.innerHTML = html;
}
