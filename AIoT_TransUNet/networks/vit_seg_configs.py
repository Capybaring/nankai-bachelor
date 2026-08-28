import ml_collections

config = ml_collections.ConfigDict()
config.patches = ml_collections.ConfigDict({"size": (32, 32)})
config.hidden_size = 768
config.transformer = ml_collections.ConfigDict()
config.transformer.mlp_dim = 3072
config.transformer.num_heads = 12
config.transformer.num_layers = 12
config.transformer.attention_dropout_rate = 0.0
config.transformer.dropout_rate = 0.1
config.classifier = "seg"
config.representation_size = None
config.resnet_pretrained_path = None
config.patch_size = 16
config.decoder_channels = (256, 128, 64, 16)
config.activation = "softmax"
config.n_skip = 0
config.n_classes = 2
