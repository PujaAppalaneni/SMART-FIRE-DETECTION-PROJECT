import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout

# Settings
img_size = (224, 224)
batch_size = 32

# Load dataset from "data/" folder
train_gen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_data = train_gen.flow_from_directory(
    "data",
    target_size=img_size,
    batch_size=batch_size,
    class_mode="sparse",
    subset="training"
)

val_data = train_gen.flow_from_directory(
    "data",
    target_size=img_size,
    batch_size=batch_size,
    class_mode="sparse",
    subset="validation"
)

# Build CNN model
model = Sequential([
    Conv2D(16, (3, 3), activation='relu', input_shape=(*img_size, 3)),
    MaxPooling2D(2, 2),
    Conv2D(32, (3, 3), activation='relu'),
    MaxPooling2D(2, 2),
    Flatten(),
    Dropout(0.3),
    Dense(64, activation='relu'),
    Dense(2, activation='softmax')  # 2 classes: Fire, Normal
])

# Compile
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(train_data, validation_data=val_data, epochs=10)

# Save the model
model.save("image_model/fire_detection_model.h5")
print("✅ Model saved to image_model/fire_detection_model.h5")
