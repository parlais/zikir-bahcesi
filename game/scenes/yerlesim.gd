class_name Yerlesim
extends RefCounted
## Bahçe yerleşimi: her asset'in adadaki sabit yuvaları. Ada yarıçapı ~6 m,
## üst yüzey y=0; kamera varsayılan olarak +z tarafından bakar.

const MODEL_DIR := "res://assets/models/"

## asset id -> yuvalar [konum, y dönüşü (derece), ölçek]
const YUVALAR := {
	"bahce_kapisi": [[Vector3(0, 0, -4.7), 0.0, 1.0]],
	"sadirvan": [[Vector3(0, 0, 0.2), 22.5, 0.85]],
	"kosk": [[Vector3(-3.3, 0, -2.0), 35.0, 1.0]],
	"hurma_agaci": [
		[Vector3(3.7, 0, -2.3), 0.0, 1.0], [Vector3(-4.3, 0, 1.9), 60.0, 0.95],
		[Vector3(4.2, 0, 1.3), 140.0, 1.05], [Vector3(2.6, 0, -4.0), 200.0, 0.9],
		[Vector3(-1.6, 0, -4.4), 260.0, 0.9], [Vector3(-2.8, 0, 3.9), 300.0, 1.0],
	],
	"lale": [
		[Vector3(-1.2, 0, 2.5), 0.0, 1.7], [Vector3(-0.6, 0, 2.6), 40.0, 1.7], [Vector3(0.0, 0, 2.5), 80.0, 1.7],
		[Vector3(0.6, 0, 2.6), 120.0, 1.7], [Vector3(1.2, 0, 2.5), 160.0, 1.7],
		[Vector3(-0.9, 0, 3.1), 200.0, 1.7], [Vector3(-0.3, 0, 3.2), 240.0, 1.7], [Vector3(0.3, 0, 3.1), 280.0, 1.7],
		[Vector3(0.9, 0, 3.2), 320.0, 1.7], [Vector3(-0.6, 0, 3.7), 10.0, 1.7], [Vector3(0.0, 0, 3.8), 50.0, 1.7],
		[Vector3(0.6, 0, 3.7), 90.0, 1.7],
	],
	"kandil": [[Vector3(1.9, 0, -4.3), 180.0, 1.2], [Vector3(-2.2, 0, 0.9), 90.0, 1.2],
		[Vector3(2.2, 0, 1.2), 0.0, 1.2], [Vector3(-0.1, 0, 4.6), 0.0, 1.2]],
	"fener_ve_kutup_yildizi": [[Vector3(1.9, 0, 3.2), 0.0, 1.6], [Vector3(-1.9, 0, 3.2), 0.0, 1.6]],
	"define_sandigi": [[Vector3(4.4, 0, -0.5), -70.0, 1.6]],
	"inci": [[Vector3(3.9, 0, 3.0), 0.0, 2.2]],
	"mercan": [[Vector3(4.6, 0, 2.5), 30.0, 1.8]],
	"sedef": [[Vector3(3.5, 0, 3.5), -20.0, 2.2]],
	"hediye_bohcasi": [[Vector3(-0.9, 0, -3.6), 20.0, 2.0]],
	"ipek_kozasi": [[Vector3(-2.3, 0, 0.0), 40.0, 2.2]],
	"ari_kovani": [[Vector3(-4.6, 0, -0.1), 60.0, 1.5]],
	"rahle_ve_kitap": [[Vector3(-3.3, 0.53, -2.0), 35.0, 1.5]],
	"tesbih": [[Vector3(-2.75, 0.53, -1.6), 0.0, 2.5]],
}
