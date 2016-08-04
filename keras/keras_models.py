from keras.regularizers import l2
from keras.models import Sequential
from keras.layers.advanced_activations import PReLU
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.normalization import BatchNormalization


def build_keras_nn( hidden_layers = [ 64, 64, 64 ], dropout_rate = 0, 
					 l2_penalty = 0.1, optimizer = 'adam' ):
	"""
	Keras Multi-layer neural network

	Fixed parameters include the activation function and
	it will always uses batch normalization after the activation.
	note that n_input and n_class are global variables that
	are not defined inside the function
	
	Parameters
	----------
	Tunable parameters are (these are the ones that are commonly tuned)
	
	hidden_layers: list
		the number of hidden layers, and the size of each hidden layer

	dropout_rate: float 0 ~ 1
		if bigger than 0, there will be a dropout layer

	l2_penalty: float
		or so called l2 regularization

	optimizer: string or keras optimizer
		method to train the network

	Returns
	-------
	model : 
		a keras model
	"""   
	model = Sequential()
	
	for index, layers in enumerate(hidden_layers):       
		if not index:
			# specify the input_dim to be the number of features for the first layer
			model.add( Dense( layers, input_dim = n_input, W_regularizer = l2(l2_penalty) ) )
		else:
			model.add( Dense( layers, W_regularizer = l2(l2_penalty) ) )
		
		# insert BatchNorm layer immediately after fully connected layers
		# and before activation layer
		model.add( BatchNormalization() )
		model.add( PReLU() )
		if dropout_rate:
			model.add( Dropout( p = dropout_rate ) )
    
	model.add( Dense(n_class) )
	model.add( Activation('softmax') )
	
	# the loss for binary and muti-class classification is different 
	loss = 'binary_crossentropy'
	if n_class > 2:
		loss = 'categorical_crossentropy'
    
	model.compile( loss = loss, optimizer = optimizer, metrics = ['accuracy'] )  
	return model


if __name__ == '__main__':
	from sklearn.grid_search import RandomizedSearchCV
	from keras.wrappers.scikit_learn import KerasClassifier

	# build the model, note that verbose is turned off here
	# number of epochs and batch size should be hyperparameters
	keras_nn = KerasClassifier( 
		build_fn = build_keras_nn, 
		nb_epoch = 15, 
		batch_size = 1024, 
		verbose = 0
	)

	# specify the options and store them inside the dictionary
	dropout_rate_opts  = [ 0, 0.2, 0.5 ]
	hidden_layers_opts = [ [ 64, 64, 64 ], [ 128, 32, 32, 32, 32 ] ]
	l2_penalty_opts = [ 0.01, 0.1, 0.5 ]
	param_dict = {
		'hidden_layers': hidden_layers_opts,
		'dropout_rate': dropout_rate_opts,  
		'l2_penalty': l2_penalty_opts
	}

	# 1. note that for randomized search, the parameter to pass the the dictionary that
	# holds the possible parameter value is `param_distributions`
	# 2. `verbose` 2 will print the class info for every cross validation, kind
	# of too much
	keras_nn_cv = RandomizedSearchCV( 
		estimator = keras_nn, 
		param_distributions = param_dict, 
		n_iter = 4, 
		cv = 5,
		verbose = 1 
	)
	# then you call .fit to your data
	# keras_nn_cv.fit( X, y_encode )
