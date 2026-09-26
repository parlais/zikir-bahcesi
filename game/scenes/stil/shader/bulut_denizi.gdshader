shader_type spatial;
// Bulut denizi: koni-dağın eteğini saran, kabarık ve yavaşça kıpırdayan bulutlar.
// Düzlem köşeleri gürültüyle kabartılır; ışık yumuşak sarılır.
render_mode blend_mix, depth_draw_opaque, cull_disabled, diffuse_lambert_wrap;

uniform vec3 acik : source_color = vec3(1.0, 0.98, 0.96);
uniform vec3 golge : source_color = vec3(0.78, 0.8, 0.95);
uniform vec3 isima : source_color = vec3(1.0, 0.9, 0.75);
uniform float isima_guc = 0.25;
uniform float kabarma = 90.0;
uniform float olcek = 0.0012;
// Kesit (K18): bulut denizi kendi ışığıyla da aydınlanır (güneş arkadan vurunca kameraya bakan
// yamaçlar gölgede kalıp düz bir alana dönüyordu)
uniform float oz_isik = 0.0;
// Kesit (K19): piksel başına kümülüs kabarcıkları; yakınlaşmada yukarıdan bakınca bulut denizi
// düz bir pembe alan gibi kalmasın. Uzakta ortalama görünüşe söner.
uniform float kabarcik = 0.0;

varying vec3 dunya;
varying float yogun;

float h3(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float g3(vec3 x) {
	vec3 i = floor(x), f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(h3(i), h3(i + vec3(1, 0, 0)), f.x), mix(h3(i + vec3(0, 1, 0)), h3(i + vec3(1, 1, 0)), f.x), f.y),
		mix(mix(h3(i + vec3(0, 0, 1)), h3(i + vec3(1, 0, 1)), f.x), mix(h3(i + vec3(0, 1, 1)), h3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float fbm(vec3 p) {
	float s = 0.0, a = 0.5;
	for (int i = 0; i < 5; i++) { s += a * g3(p); p = p * 2.03 + vec3(1.7, 9.2, 3.3); a *= 0.5; }
	return s;
}
float yuk(vec2 xz) {
	float n = fbm(vec3(xz * olcek, TIME * 0.01));
	return pow(clamp(n * 1.35 - 0.2, 0.0, 1.0), 1.6);
}

void vertex() {
	vec3 w = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	float h = yuk(w.xz);
	float e = 30.0;
	float hx = yuk(w.xz + vec2(e, 0.0));
	float hz = yuk(w.xz + vec2(0.0, e));
	VERTEX.y += h * kabarma;
	NORMAL = normalize(vec3(-(hx - h) * kabarma / e, 1.0, -(hz - h) * kabarma / e));
	yogun = h;
	dunya = w;
}

void fragment() {
	float ince = fbm(vec3(dunya.xz * olcek * 6.0, TIME * 0.02));
	float t = yogun * 1.2 + ince * 0.4;
	if (kabarcik > 0.0) {
		// İki ölçekte yuvarlak kabarcıklar, aralarında gölgeli yarıklar
		vec2 q = dunya.xz * olcek * 14.0;
		float sonum = 1.0 - smoothstep(0.35, 1.2, length(fwidth(q)));
		float b1 = smoothstep(0.32, 0.72, fbm(vec3(q, TIME * 0.02)));
		float b2 = smoothstep(0.3, 0.75, fbm(vec3(q * 3.3 + 7.1, TIME * 0.03)));
		float kab = mix(0.5, b1 * 0.7 + b2 * 0.3, sonum);
		t = mix(t, t * 0.75 + (kab - 0.5) * 0.9 + 0.12, kabarcik);
	}
	vec3 c = mix(golge, acik, clamp(t, 0.0, 1.0));
	ALBEDO = c;
	ROUGHNESS = 1.0;
	SPECULAR = 0.0;
	EMISSION = isima * isima_guc * (0.4 + yogun) + c * oz_isik * (0.55 + 0.6 * clamp(yogun * 1.3 + ince * 0.5 - 0.3, 0.0, 1.0));
	ALBEDO = c * (1.0 - 0.7 * oz_isik);
}
