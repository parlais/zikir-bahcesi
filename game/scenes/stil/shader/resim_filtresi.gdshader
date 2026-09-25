shader_type canvas_item;
// Yağlı boya filtresi (K9). 3B sahne bir SubViewport'a çizilir; bu shader onu ekrana
// boyar:
//   1. Yönlü (anizotropik) Kuwahara: kenarları izleyen fırça lekeleri
//      (Kyprianidis vd. 2010, polinom ağırlıklı 8 dilim; tek geçişli yaklaşım)
//   2. Fırça izi: leke yönünde uzayan çizgi dokusu
//   3. Boya kabartması (impasto): fırça izinden ışık alan kabartı
//   4. Tuval dokusu, ince gren, sıcak sır, doygunluk, hafif vinyet

uniform float yaricap = 5.0;          // leke boyu (800 piksel genişliğe göre; çözünürlükle ölçeklenir)
uniform float anizotropi = 1.0;
uniform float keskinlik = 8.0;         // dilim seçiciliği (q)
uniform float firca = 0.06;            // fırça izi şiddeti
uniform float firca_olcek = 1.0;
uniform float impasto = 0.5;
uniform float tuval = 0.04;
uniform float gren = 0.02;
uniform float doygunluk = 1.05;
uniform float kontrast = 1.04;
uniform vec3 sicak : source_color = vec3(1.0, 0.96, 0.88);
uniform vec3 golge_ton : source_color = vec3(0.93, 0.92, 1.0);
uniform float vinyet = 0.15;

const int N = 6;

float parlaklik(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

float h2(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float g2(vec2 p) {
	vec2 i = floor(p), f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(h2(i), h2(i + vec2(1, 0)), f.x), mix(h2(i + vec2(0, 1)), h2(i + vec2(1, 1)), f.x), f.y);
}

vec3 sobel(sampler2D tex, vec2 uv, vec2 px) {
	float a = parlaklik(texture(tex, uv + px * vec2(-1, -1)).rgb);
	float b = parlaklik(texture(tex, uv + px * vec2(0, -1)).rgb);
	float c = parlaklik(texture(tex, uv + px * vec2(1, -1)).rgb);
	float d = parlaklik(texture(tex, uv + px * vec2(-1, 0)).rgb);
	float f = parlaklik(texture(tex, uv + px * vec2(1, 0)).rgb);
	float g = parlaklik(texture(tex, uv + px * vec2(-1, 1)).rgb);
	float h = parlaklik(texture(tex, uv + px * vec2(0, 1)).rgb);
	float i = parlaklik(texture(tex, uv + px * vec2(1, 1)).rgb);
	float gx = (c + 2.0 * f + i) - (a + 2.0 * d + g);
	float gy = (g + 2.0 * h + i) - (a + 2.0 * b + c);
	return vec3(gx * gx, gx * gy, gy * gy);
}

void fragment() {
	vec2 px = TEXTURE_PIXEL_SIZE;
	vec2 uv = UV;
	vec3 orijinal = texture(TEXTURE, uv).rgb;

	// 1) Yapı tensörü (dört noktada Sobel, ortalama) -> fırça yönü ve anizotropi
	vec3 st = sobel(TEXTURE, uv + px * vec2(-1.5, -1.5), px) + sobel(TEXTURE, uv + px * vec2(1.5, -1.5), px)
		+ sobel(TEXTURE, uv + px * vec2(-1.5, 1.5), px) + sobel(TEXTURE, uv + px * vec2(1.5, 1.5), px);
	st *= 0.25;
	float te = st.x, tf = st.y, tg = st.z;
	float kok = sqrt((te - tg) * (te - tg) + 4.0 * tf * tf);
	float l1 = 0.5 * (te + tg + kok);
	float l2 = 0.5 * (te + tg - kok);
	vec2 t = vec2(l1 - te, -tf);
	t = length(t) > 1e-6 ? normalize(t) : vec2(0.0, 1.0);
	float A = (l1 + l2 > 1e-6) ? (l1 - l2) / (l1 + l2) : 0.0;
	// Düz alanlarda (gök, çayır) yön gürültülüdür: varsayılan çapraz fırça yönüne karıştır
	float guven = smoothstep(0.05, 0.4, l1 + l2) * smoothstep(0.15, 0.5, A);
	float aci0 = (g2(uv * 2.2 + 3.1) - 0.5) * 3.0 + (g2(uv * 6.0 + 9.7) - 0.5) * 0.8 + 0.35;
	vec2 t0 = vec2(cos(aci0), sin(aci0));
	if (dot(t, t0) < 0.0) { t = -t; }
	t = normalize(mix(t0, t, guven) + vec2(1e-5));
	A *= guven;
	float phi = -atan(t.y, t.x);
	float r = yaricap * (1.0 / px.x) / 800.0;
	float a = r * clamp((anizotropi + A) / anizotropi, 0.1, 2.0);
	float b = r * clamp(anizotropi / (anizotropi + A), 0.1, 2.0);
	float cp = cos(phi), sp = sin(phi);
	mat2 R = mat2(vec2(cp, -sp), vec2(sp, cp));

	// 2) Polinom ağırlıklı 8 dilimli Kuwahara (birim diskte örnekleme)
	vec4 m[8];
	vec3 s[8];
	for (int k = 0; k < 8; k++) { m[k] = vec4(0.0); s[k] = vec3(0.0); }
	float zeta = 0.35;
	float sifir = 0.58;
	float eta = (zeta + cos(sifir)) / (sin(sifir) * sin(sifir));
	for (int j = -N; j <= N; j++) {
		for (int i = -N; i <= N; i++) {
			vec2 v = vec2(float(i), float(j)) / float(N);
			if (dot(v, v) > 1.0) { continue; }
			vec2 ofs = R * (v * vec2(a, b));
			vec2 suv = uv + ofs * px;
			vec3 c = texture(TEXTURE, suv).rgb;
			// Sabit boya gürültüsü: filtre bunu kenar yönünde sürükleyerek fırça darbesine çevirir
			vec2 sp = suv / px * (800.0 * px.x) * firca_olcek;
			c *= 1.0 + firca * ((g2(sp * 0.22) - 0.5) * 1.4 + (g2(sp * 0.07 + 4.3) - 0.5) * 0.8);
			float w[8];
			float z;
			float toplam = 0.0;
			float vxx = zeta - eta * v.x * v.x;
			float vyy = zeta - eta * v.y * v.y;
			z = max(0.0, v.y + vxx); w[0] = z * z; toplam += w[0];
			z = max(0.0, -v.x + vyy); w[2] = z * z; toplam += w[2];
			z = max(0.0, -v.y + vxx); w[4] = z * z; toplam += w[4];
			z = max(0.0, v.x + vyy); w[6] = z * z; toplam += w[6];
			vec2 u = 0.70710678 * vec2(v.x - v.y, v.x + v.y);
			vxx = zeta - eta * u.x * u.x;
			vyy = zeta - eta * u.y * u.y;
			z = max(0.0, u.y + vxx); w[1] = z * z; toplam += w[1];
			z = max(0.0, -u.x + vyy); w[3] = z * z; toplam += w[3];
			z = max(0.0, -u.y + vxx); w[5] = z * z; toplam += w[5];
			z = max(0.0, u.x + vyy); w[7] = z * z; toplam += w[7];
			float g = exp(-3.125 * dot(v, v)) / max(toplam, 1e-6);
			for (int k = 0; k < 8; k++) {
				float wk = w[k] * g;
				m[k] += vec4(c * wk, wk);
				s[k] += c * c * wk;
			}
		}
	}
	vec3 sonuc = vec3(0.0);
	float wt = 0.0;
	for (int k = 0; k < 8; k++) {
		if (m[k].w <= 1e-6) { continue; }
		vec3 ort = m[k].rgb / m[k].w;
		vec3 sap = abs(s[k] / m[k].w - ort * ort);
		float sigma2 = sap.r + sap.g + sap.b;
		float w = 1.0 / (1.0 + pow(1000.0 * sigma2, 0.5 * keskinlik));
		sonuc += ort * w;
		wt += w;
	}
	vec3 col = wt > 0.0 ? sonuc / wt : orijinal;

	// 3) Boya kabartması (impasto): leke kenarları ışık alır
	float yuk = parlaklik(col) * 1.5;
	vec2 egim = vec2(dFdx(yuk), dFdy(yuk));
	col *= 1.0 + impasto * clamp(-egim.x * 0.8 - egim.y * 1.2, -0.12, 0.12);

	// 4) Tuval, gren, renk
	vec2 pp = uv / px;
	float dokuma = sin(pp.x * 1.35) * sin(pp.y * 1.35);
	col *= 1.0 + tuval * (dokuma * 0.6 + (g2(pp * 0.35) - 0.5) * 0.8);
	col += (h2(pp + fract(TIME)) - 0.5) * gren;
	float l = parlaklik(col);
	col = mix(vec3(l), col, doygunluk);
	col = (col - 0.5) * kontrast + 0.5;
	col *= mix(golge_ton, sicak, smoothstep(0.15, 0.85, l));
	vec2 v = uv - 0.5;
	col *= 1.0 - vinyet * dot(v, v) * 2.0;
	COLOR = vec4(max(col, vec3(0.0)), 1.0);
}
