shader_type spatial;
// Şadırvan ve havuzlar için sade su yüzeyi: hafif dalga, kenarda parlama.
render_mode blend_mix, cull_disabled, specular_schlick_ggx;

uniform vec3 derin : source_color = vec3(0.16, 0.45, 0.62);
uniform vec3 sig : source_color = vec3(0.45, 0.78, 0.88);
uniform float dalga = 0.012;

void vertex() {
	float t = TIME * 1.4;
	VERTEX.y += sin(VERTEX.x * 6.0 + t) * dalga + cos(VERTEX.z * 5.0 + t * 1.3) * dalga;
}

void fragment() {
	float f = pow(1.0 - clamp(dot(NORMAL, VIEW), 0.0, 1.0), 2.0);
	float halka = 0.5 + 0.5 * sin(length(UV - 0.5) * 40.0 - TIME * 2.0);
	ALBEDO = mix(derin, sig, f * 0.8 + halka * 0.08);
	ROUGHNESS = 0.08;
	METALLIC = 0.0;
	SPECULAR = 0.7;
	ALPHA = 0.88;
}
