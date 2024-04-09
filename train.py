import tensorflow.keras as keras 

# keras 
from keras.optimizers import Adam
from keras.layers import Dense, Dropout, LSTM, Input


from preprocess import generating_training_sequences, SEQUENCE_LENGTH

SAVE_MODEL_PATH = 'model.h5'
OUTPUT_UNITS = 38 # Equal to vocabulary size
EPOCHS = 50
BATCH_SIZE =  64 # Amout of samples 
LOSS = "sparse_categorical_crossentropy"
LEARNING_RATE = 0.001
NUM_UNITS = [256]


def build_model(output_units, num_units, loss, learning_rate):
    # Create the model architecture using functional API 
    # None enables us to have as many timestamps as we want 
    input = Input(shape=(None, output_units))
    x = LSTM(num_units[0])(input)
    x = Dropout(0.2)(x) # Used to avoid overfitting

    output = Dense(output_units, activation='softmax')(x)

    model = keras.Model(input, output)

    # Compile Model 
    model.compile(loss=loss, 
                  optimizer = Adam(learning_rate = learning_rate), 
                  metrics = ['accuracy']
                  )
    
    model.summary()

    return model

def train(output_units = OUTPUT_UNITS, num_units = NUM_UNITS, loss = LOSS, learning_rate = LEARNING_RATE):
    # Generate the training sequences
    inputs, targets = generating_training_sequences(SEQUENCE_LENGTH)

    # build the network 
    model = build_model(output_units, num_units, loss, learning_rate)    

    # Train the model 
    model.fit(inputs, targets, epochs=EPOCHS, batch_size = BATCH_SIZE)

    # Save the model 
    model.save(SAVE_MODEL_PATH)

if __name__ == "__main__":
    train()