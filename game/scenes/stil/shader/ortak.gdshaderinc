// Stil shader'larının ortak parçası: renk düzeltme, toon/sarma ışık, yaprak
// geçirgenliği, kenar parlaması ve gürültü. Stil profilleri bu uniform'ları ayarlar.

uniform float toon : hint_range(0.0, 1.0) = 0.0;      // 0 gerçekçi, 1 çizgi film geçişi
uniform float toon_esik : hint_range(0.0, 1.0) = 0.45;
uniform float toon_yumusak : hint_range(0.0, 0.5) = 0.08;
uniform vec3 golge_renk : source_color = vec3(0.62, 0.66, 0.88);  // toon gölgesinin rengi
uniform float doygunluk = 1.0;
uniform vec3 renk_carpan : source_color = vec3(1.0);
uniform float parlaklik = 1.0;
uniform float sarma : hint_range(0.0, 1.0) = 0.0;     // ışığın gölge tarafa sarması
uniform float gecirgenlik = 0.0;                        // arkadan gelen ışığın yapraktan geçişi
uniform vec3 gecirgen_renk : source_color = vec3(1.0, 0.9, 0.5);
uniform float kenar = 0.0;                              // kenar (rim) parlaması
uniform vec3 kenar_renk : source_color = vec3(1.0, 0.92, 0.75);
uniform float spek = 0.25;
uniform float spek_sertlik = 24.0;
// Gölgenin ne kadarının alınacağı (1 tam). Yaprak kartları yarı alır: sık taçta kartlar
// birbirini gölgeleyince taç kapkara bir siluete dönüyordu (K15).
uniform float golge_alma : hint_range(0.0, 1.0) = 1.0;

vec3 zb_renk(vec3 c) {
	float l = dot(c, vec3(0.2126, 0.7152, 0.0722));
	return max(mix(vec3(l), c, doygunluk), vec3(0.0)) * renk_carpan * parlaklik;
}

float zb_hash(vec3 p) {
	p = fract(p * 0.3183099 + 0.1);
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float zb_gurultu(vec3 x) {
	vec3 i = floor(x);
	vec3 f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(zb_hash(i), zb_hash(i + vec3(1, 0, 0)), f.x),
			mix(zb_hash(i + vec3(0, 1, 0)), zb_hash(i + vec3(1, 1, 0)), f.x), f.y),
		mix(mix(zb_hash(i + vec3(0, 0, 1)), zb_hash(i + vec3(1, 0, 1)), f.x),
			mix(zb_hash(i + vec3(0, 1, 1)), zb_hash(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}

float zb_fbm(vec3 p) {
	float s = 0.0;
	float a = 0.5;
	for (int i = 0; i < 4; i++) {
		s += a * zb_gurultu(p);
		p *= 2.03;
		a *= 0.5;
	}
	return s;
}

void light() {
	float ndl = dot(NORMAL, LIGHT);
	float w = clamp((ndl + sarma) / (1.0 + sarma), 0.0, 1.0);
	float zb_golge = mix(1.0, ATTENUATION, golge_alma);
	float yumusak = w * zb_golge;
	float kademe = smoothstep(toon_esik - toon_yumusak, toon_esik + toon_yumusak, yumusak);
	float d = mix(yumusak, kademe, toon);
	vec3 ton = mix(vec3(1.0), mix(golge_renk, vec3(1.0), d), toon);
	DIFFUSE_LIGHT += LIGHT_COLOR * d * ton / PI;
	// Toon'da gölge tarafı tamamen kararmasın: gölge rengiyle doldur
	DIFFUSE_LIGHT += LIGHT_COLOR * golge_renk * (1.0 - d) * toon * 0.18 / PI;
	if (gecirgenlik > 0.0) {
		float arka = pow(clamp(dot(VIEW, -LIGHT), 0.0, 1.0), 3.0);
		DIFFUSE_LIGHT += LIGHT_COLOR * gecirgen_renk * arka * gecirgenlik * mix(1.0, zb_golge, 0.6) / PI;
	}
	vec3 h = normalize(LIGHT + VIEW);
	float s = pow(clamp(dot(NORMAL, h), 0.0, 1.0), spek_sertlik) * spek;
	s = mix(s, step(0.5, s) * spek, toon);
	SPECULAR_LIGHT += LIGHT_COLOR * s * ATTENUATION;
}
