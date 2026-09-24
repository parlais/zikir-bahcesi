shader_type sky;
// Gökyüzü: yükseklik geçişi, güneş ve hale, akan bulutlar, yıldızlar ve hilal.

uniform vec3 tepe : source_color = vec3(0.24, 0.5, 0.86);
uniform vec3 ufuk : source_color = vec3(0.86, 0.9, 0.95);
uniform vec3 alt : source_color = vec3(0.6, 0.66, 0.72);
uniform float ufuk_kalin = 0.35;
uniform vec3 gunes_renk : source_color = vec3(1.0, 0.92, 0.75);
uniform float gunes_boyut = 1.0;
uniform float gunes_hale = 0.35;
uniform float gunes_parlak = 12.0;
uniform float bulut = 0.5;               // örtü (0 açık, 1 kapalı)
uniform float bulut_olcek = 1.0;
uniform vec3 bulut_acik : source_color = vec3(1.0);
uniform vec3 bulut_golge : source_color = vec3(0.72, 0.76, 0.86);
uniform float yildiz = 0.0;
uniform float ay = 0.0;
uniform vec3 ay_yon = vec3(0.4, 0.35, -0.85);
uniform float parlaklik = 1.0;

float h2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float g2(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h2(i), h2(i + vec2(1, 0)), f.x), mix(h2(i + vec2(0, 1)), h2(i + vec2(1, 1)), f.x), f.y);
}
float fbm(vec2 p) {
	float s = 0.0, a = 0.5;
	for (int i = 0; i < 6; i++) { s += a * g2(p); p = p * 2.02 + vec2(1.7, 9.2); a *= 0.5; }
	return s;
}

void sky() {
	vec3 d = EYEDIR;
	float y = d.y;
	vec3 c = mix(ufuk, tepe, pow(clamp(y / max(ufuk_kalin, 0.01), 0.0, 1.0), 0.6));
	c = mix(c, tepe, smoothstep(ufuk_kalin, 1.0, y) * 0.6);
	if (y < 0.0) {
		c = mix(ufuk, alt, clamp(-y * 4.0, 0.0, 1.0));
	}
	vec3 gy = LIGHT0_ENABLED ? LIGHT0_DIRECTION : vec3(0.0, 1.0, 0.0);
	float sd = clamp(dot(d, gy), 0.0, 1.0);
	float disk = smoothstep(1.0 - 0.00015 * gunes_boyut * gunes_boyut * 8.0, 1.0 - 0.00005 * gunes_boyut, sd);
	c += gunes_renk * (pow(sd, 6.0) * gunes_hale + pow(sd, 90.0) * gunes_hale * 1.5);

	if (yildiz > 0.0 && y > 0.0) {
		vec2 sp = d.xz / (y + 0.35) * 90.0;
		float st = step(0.985, h2(floor(sp))) * smoothstep(0.35, 0.0, length(fract(sp) - 0.5));
		c += vec3(0.9, 0.92, 1.0) * st * yildiz * smoothstep(0.0, 0.25, y);
	}
	if (ay > 0.0) {
		vec3 ay_d = normalize(ay_yon);
		float a1 = dot(d, ay_d);
		vec3 kay = normalize(ay_d + vec3(0.012, 0.006, 0.0));
		float a2 = dot(d, kay);
		float hilal = smoothstep(0.99955, 0.9997, a1) * (1.0 - smoothstep(0.99955, 0.9997, a2));
		c += vec3(1.0, 0.95, 0.82) * hilal * ay * 3.0 + vec3(0.6, 0.65, 0.9) * pow(clamp(a1, 0.0, 1.0), 400.0) * ay * 0.4;
	}
	if (bulut > 0.0 && y > 0.0) {
		vec2 bp = d.xz / (y + 0.12) * 0.9 * bulut_olcek + vec2(TIME * 0.004, 0.0);
		float n = fbm(bp);
		float kaplama = smoothstep(1.0 - bulut, 1.0 - bulut + 0.35, n);
		float ic = fbm(bp * 1.8 + 3.0);
		vec3 bc = mix(bulut_golge, bulut_acik, clamp(ic * 1.2 + sd * 0.4, 0.0, 1.0));
		bc += gunes_renk * pow(sd, 8.0) * 0.6;
		c = mix(c, bc, kaplama * smoothstep(0.0, 0.12, y));
	}
	c += gunes_renk * disk * gunes_parlak;
	COLOR = c * parlaklik;
}
