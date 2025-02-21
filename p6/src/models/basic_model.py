from models.model import Model
from tensorflow.keras import Sequential, layers
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Flatten, Dense, Dropout
from tensorflow.keras.layers.experimental.preprocessing import Rescaling
from tensorflow.keras.optimizers import RMSprop, Adam

class BasicModel(Model):
    def _define_model(self, input_shape, categories_count):
        model = Sequential()
        
        # Rescaling layer: normalize pixel values [0..255] -> [0..1]
        model.add(Rescaling(scale=1./255, input_shape=input_shape))
        
        # First Convolution + Pooling block
        model.add(Conv2D(filters=24, kernel_size=(3, 3), activation='relu', padding='same'))
        model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
        # Dropout can help reduce overfitting
        model.add(Dropout(0.1))

        # Second Convolution + Pooling block
        model.add(Conv2D(filters=24, kernel_size=(3, 3), activation='relu', padding='same'))
        model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
        model.add(Dropout(0.1))

        # Third Convolution + Pooling block (optional, can remove or add more)
        model.add(Conv2D(filters=24, kernel_size=(3, 3), activation='relu', padding='same'))
        model.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
        model.add(Dropout(0.1))
        
        # Flatten + fully-connected layers
        model.add(Flatten())
        
        # A Dense layer with ReLU
        model.add(Dense(16, activation='relu'))
        model.add(Dropout(0.2))  # higher dropout can help if overfitting

        # Output layer: categories_count classes, softmax
        model.add(Dense(categories_count, activation='softmax'))

        self.model = model
    
    def _compile_model(self):
        self.model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        print("Compile done")
        self.model.summary()

