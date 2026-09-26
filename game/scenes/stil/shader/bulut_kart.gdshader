shader_type spatial;
// Bulut kümeleri (Faz 2a, K18): çağlayanların indiği bulutlar, merdivenin ucu, gökte süzülen
// kümeler ve kesitte her katın tavanının altındaki kuşak. Her kart kameraya dönen bir
// dörtgendir; bütün kartlar tek çizimdir (MultiMesh). Renk bulut_renk'ten (profil).
// Kesitte (zb_kesit) katın pusunu alır ve uzaktan pembe-gri lekelere dönmesin diye aydınlanır;
// içeride görünüş eski StandardMaterial kartlarıyla aynıdır.
// INSTANCE_CUSTOM.r: kümedeki yüksekliğe göre ton (0 gölge, 1 açık).
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never;
#include "res://scenes/stil/shader/ortak.gdshaderinc"
#include "res://scenes/stil/shader/kesit.gdshaderinc"

uniform sampler2D doku : source_color, filter_linear_mipmap;
uniform vec4 acik : source_color = vec4(1.0);
uniform vec4 golge : source_color = vec4(0.8, 0.84, 0.95, 1.0);
uniform float saydam = 0.72;

varying vec3 dunya;
varying float f;

void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0),
		vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0),
		vec4(0.0, 0.0, 0.0, 1.0));
	dunya = (INV_VIEW_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	f = INSTANCE_CUSTOM.r;
}

void fragment() {
	vec4 t = texture(doku, UV);
	vec3 ic = mix(golge.rgb, acik.rgb, f) * t.rgb;
	vec3 dis = mix(mix(golge.rgb, acik.rgb, 0.55), acik.rgb * 1.08, f) * mix(t.rgb, vec3(1.0), 0.35);
	vec3 c = mix(ic, dis, zb_kesit);
	float p = zb_pus_miktar(dunya);
	ALBEDO = mix(c, zb_pus_renk(dunya) * 1.06, p * 0.85);
	ALPHA = t.a * saydam;
}
