shader_type spatial;
// Kanal ve havuz suyu: opak ve çok pürüzsüz yüzey; Forward+ ekran uzayı
// yansıması (SSR) köşkü ve selvileri suya yansıtır. Dalgalar normalle verilir.
render_mode blend_mix, depth_draw_opaque, cull_back;

uniform vec3 derin : source_color = vec3(0.04, 0.22, 0.28);
uniform vec3 sig : source_color = vec3(0.12, 0.55, 0.58);
uniform float dalga_olcek = 1.6;
uniform float dalga_guc = 0.35;
uniform float isima_guc = 0.0;
uniform vec3 isima : source_color = vec3(0.1, 0.7, 0.75);
uniform vec2 akis = vec2(0.0);        // ırmaklarda dalgaların akış hızı (m/sn, dünya xz)
uniform float puruz = 0.03;

varying vec3 dunya;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

vec2 egim(vec2 p, float t) {
	vec2 g = vec2(0.0);
	g += vec2(cos(p.x * 1.3 + t), 0.0) * 0.5;
	g += vec2(0.0, cos(p.y * 1.7 - t * 1.2)) * 0.4;
	g += vec2(cos((p.x + p.y) * 2.9 + t * 1.7)) * 0.2;
	g += vec2(-cos((p.x - p.y) * 4.3 - t * 2.1), cos((p.x - p.y) * 4.3 - t * 2.1)) * 0.1;
	return g;
}

void fragment() {
	vec2 g = egim((dunya.xz - akis * TIME) * dalga_olcek, TIME * 1.1) * dalga_guc;
	vec3 n_dunya = normalize(vec3(-g.x, 1.0, -g.y));
	NORMAL = normalize((VIEW_MATRIX * vec4(n_dunya, 0.0)).xyz);
	float f = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 4.0);
	float kostik = pow(0.5 + 0.5 * sin(dunya.x * 7.0 + TIME) * sin(dunya.z * 6.0 - TIME * 1.3), 6.0);
	ALBEDO = mix(sig, derin, f) + kostik * 0.05;
	ROUGHNESS = puruz;
	METALLIC = 0.0;
	SPECULAR = 0.9;
	EMISSION = isima * isima_guc * (0.6 + kostik);
}
