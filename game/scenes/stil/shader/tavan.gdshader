shader_type spatial;
// Tabakaların göğü (K10): kesit görünümünde tabakaların tavanı ve arka gök perdesi.
// Kendi ışığıyla parlar (gölge almaz); renk köşe renginden, üstünde yumuşak bulut lekeleri.
render_mode unshaded, cull_back;
#include "res://scenes/stil/shader/ortak.gdshaderinc"

uniform float guc = 1.0;
uniform float bulut = 0.3;
uniform float bulut_olcek = 0.004;

varying vec3 dunya;

void vertex() {
	dunya = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float n = zb_fbm(dunya * bulut_olcek + vec3(0.0, 0.0, TIME * 0.002));
	vec3 c = mix(COLOR.rgb, vec3(1.0, 0.99, 0.96), smoothstep(0.5, 0.78, n) * bulut);
	ALBEDO = zb_renk(c) * guc;
}
