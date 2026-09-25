shader_type sky;
// Cennet göğü (K5): güneş diski yok; ışık yumuşak ve kaynağı belirsiz. Üst
// derecelerin ardından gelen geniş bir nur parıltısı, kabarık kümülüs bulutları.
// kozmik = 1: katlı koni-dağın dıştan görünümü için ışıklı, pastel bir boşluk
// (Küllî Kaideler 2: galaksiler ve güneşler bu bahçenin çiçekleri gibidir).

uniform vec3 tepe : source_color = vec3(0.28, 0.56, 0.92);
uniform vec3 orta : source_color = vec3(0.56, 0.78, 0.97);
uniform vec3 ufuk : source_color = vec3(0.98, 0.93, 0.85);
uniform vec3 alt : source_color = vec3(0.9, 0.87, 0.84);
uniform float ufuk_kalin = 0.2;
uniform vec3 nur_yon = vec3(0.0, 0.25, -1.0);
// Işık geçişi (K12): ikinci parıltı. nur_karisim 0'da yalnız nur_yon, 1'de yalnız
// nur_yon_b parlar; arada biri yerinde söner, öbürü yerinde belirir (gezinmez).
uniform vec3 nur_yon_b = vec3(0.0, 0.25, -1.0);
uniform float nur_karisim = 0.0;
uniform vec3 nur_renk : source_color = vec3(1.0, 0.9, 0.7);
uniform float nur_guc = 1.0;          // geniş parıltı
uniform float nur_cekirdek = 1.5;     // yoğun merkez
uniform float bulut = 0.45;           // örtü
uniform float bulut_olcek = 1.0;
uniform float bulut_yukseklik = 0.35; // bulutların yoğunlaştığı yükseklik (yön.y)
uniform vec3 bulut_acik : source_color = vec3(1.0, 1.0, 1.0);
uniform vec3 bulut_golge : source_color = vec3(0.7, 0.77, 0.92);
uniform vec3 bulut_kenar : source_color = vec3(1.0, 0.92, 0.78);
uniform float kozmik = 0.0;
uniform vec3 bulutsu_a : source_color = vec3(1.0, 0.78, 0.88);
uniform vec3 bulutsu_b : source_color = vec3(0.72, 0.82, 1.0);
uniform float parilti = 0.0;          // kozmik boşlukta çiçek gibi ışık noktaları
uniform float parlaklik = 1.0;

float h2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float g2(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h2(i), h2(i + vec2(1, 0)), f.x), mix(h2(i + vec2(0, 1)), h2(i + vec2(1, 1)), f.x), f.y);
}
float fbm(vec2 p) {
	float s = 0.0, a = 0.5;
	for (int i = 0; i < 6; i++) { s += a * g2(p); p = p * 2.03 + vec2(1.7, 9.2); a *= 0.5; }
	return s;
}
float h3(vec3 p) { return fract(sin(dot(p, vec3(127.1, 311.7, 74.7))) * 43758.5453); }
float g3(vec3 x) {
	vec3 i = floor(x), f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(h3(i), h3(i + vec3(1, 0, 0)), f.x), mix(h3(i + vec3(0, 1, 0)), h3(i + vec3(1, 1, 0)), f.x), f.y),
		mix(mix(h3(i + vec3(0, 0, 1)), h3(i + vec3(1, 0, 1)), f.x), mix(h3(i + vec3(0, 1, 1)), h3(i + vec3(1, 1, 1)), f.x), f.y), f.z);
}
float fbm3(vec3 p) {
	float s = 0.0, a = 0.5;
	for (int i = 0; i < 5; i++) { s += a * g3(p); p = p * 2.02 + vec3(3.1, 1.7, 5.3); a *= 0.5; }
	return s;
}

vec3 gunduz(vec3 d) {
	float y = d.y;
	vec3 c = mix(ufuk, orta, smoothstep(0.0, ufuk_kalin, y));
	c = mix(c, tepe, smoothstep(ufuk_kalin, 1.0, y));
	if (y < 0.0) {
		c = mix(ufuk, alt, clamp(-y * 5.0, 0.0, 1.0));
	}
	return c;
}

vec3 bosluk(vec3 d, float nd) {
	// Nura yakın sıcak beyaz-altın, uzaklaştıkça pembe, lavanta ve açık mavi
	vec3 c = mix(bulutsu_b, bulutsu_a, smoothstep(-0.3, 0.6, nd));
	c = mix(c, ufuk, smoothstep(0.82, 0.995, nd));
	float n = fbm3(d * 2.2 + vec3(0.0, TIME * 0.002, 0.0));
	float n2 = fbm3(d * 5.0 + 11.0);
	c = mix(c, bulutsu_a * 1.1, smoothstep(0.5, 0.8, n) * 0.35);
	c = mix(c, bulutsu_b * 1.08, smoothstep(0.55, 0.8, n2) * 0.25);
	c = mix(c, tepe, smoothstep(0.2, 1.0, d.y) * 0.25 * (1.0 - smoothstep(0.4, 0.9, nd)));
	if (parilti > 0.0) {
		vec2 a = vec2(atan(d.x, d.z), asin(clamp(d.y, -1.0, 1.0))) * 70.0;
		vec2 hc = floor(a);
		float r = h2(hc);
		float benek = smoothstep(0.42, 0.0, length(fract(a) - 0.5 - (vec2(h2(hc + 3.1), h2(hc + 7.7)) - 0.5) * 0.5));
		vec3 renk = r > 0.995 ? vec3(1.0, 0.75, 0.85) : (r > 0.99 ? vec3(0.75, 0.9, 1.0) : vec3(1.0, 0.95, 0.8));
		c += renk * benek * step(0.985, r) * parilti * (0.6 + 0.4 * sin(TIME * 0.7 + r * 50.0));
	}
	return c;
}

void sky() {
	vec3 d = EYEDIR;
	vec3 ny = normalize(nur_yon);
	vec3 nyb = normalize(nur_yon_b);
	float nda = dot(d, ny);
	float ndb = dot(d, nyb);
	float nd = mix(nda, ndb, nur_karisim);
	vec3 c = mix(gunduz(d), bosluk(d, nd), kozmik);
	// Nur parıltısı: geniş hale ve yumuşak çekirdek (disk yok)
	float ya = clamp(nda, 0.0, 1.0);
	float yb = clamp(ndb, 0.0, 1.0);
	float us_hale = mix(5.0, 14.0, kozmik);
	float us_cekirdek = mix(40.0, 180.0, kozmik);
	float hale = mix(pow(ya, us_hale), pow(yb, us_hale), nur_karisim);
	float cekirdek = mix(pow(ya, us_cekirdek), pow(yb, us_cekirdek), nur_karisim);
	c += nur_renk * (hale * nur_guc * 0.5 + cekirdek * nur_cekirdek);

	if (bulut > 0.0 && d.y > 0.0 && kozmik < 0.99) {
		vec2 bp = d.xz / (d.y + 0.1) * 0.55 * bulut_olcek + vec2(TIME * 0.003, TIME * 0.001);
		float n = fbm(bp);
		float yogun = smoothstep(1.0 - bulut, 1.0 - bulut + 0.28, n);
		// Işığa bakan kenarlar açık, gölge tarafı mavimsi (2B kümülüs gölgelemesi)
		vec2 lyon = normalize(mix(ny.xz, nyb.xz, nur_karisim) + vec2(1e-4)) * 0.06;
		float n2 = fbm(bp + lyon);
		float isik = clamp(0.55 + (n - n2) * 5.0, 0.0, 1.0);
		float ic = fbm(bp * 2.3 + 5.0);
		vec3 bc = mix(bulut_golge, bulut_acik, clamp(isik * 0.8 + ic * 0.35, 0.0, 1.0));
		bc += bulut_kenar * (mix(pow(ya, 6.0), pow(yb, 6.0), nur_karisim) * 0.8 + (1.0 - yogun) * 0.3 * isik);
		float katman = smoothstep(0.02, 0.12, d.y) * (1.0 - smoothstep(bulut_yukseklik, bulut_yukseklik + 0.45, d.y) * 0.75);
		c = mix(c, bc, yogun * katman * (1.0 - kozmik));
	}
	COLOR = c * parlaklik;
}
