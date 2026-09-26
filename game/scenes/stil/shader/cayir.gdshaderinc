// Çayır (K20): ovanın rüzgâr dalgası ve sabâ halkası. Zemin ve çimen tutamları aynı
// bantları görür: rüzgâr ovada açık bantlar hâlinde geçer, çimen o bantlarda yatar.
// ortak.gdshaderinc'ten sonra eklenir (zb_fbm).

// Sabâ halkası: her zikirde Tûbâ çekirdeğinden ovaya yayılan nur ve rüzgâr halkası
// (x, z merkez; z yarıçap m; w güç 0-1). Betik (CennetSahnesi._saba) sürer.
global uniform vec4 zb_dalga;

float zb_ruzgar_bandi(vec3 zb_p, float zb_t) {
	float zb_yol = dot(zb_p.xz, vec2(0.8, -0.6)) * 0.028 - zb_t * 0.35 + zb_fbm(zb_p * 0.006) * 5.0;
	return smoothstep(0.35, 1.0, sin(zb_yol)) * smoothstep(0.3, 0.7, zb_fbm(zb_p * 0.012 + vec3(zb_t * 0.01, 0.0, 0.0)));
}

float zb_halka(vec2 zb_p) {
	float zb_d = length(zb_p - zb_dalga.xy);
	float zb_x = (zb_d - zb_dalga.z) / 7.0;
	return exp(-zb_x * zb_x) * zb_dalga.w;
}
