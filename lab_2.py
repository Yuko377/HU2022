from mindspore import context
import numpy as np
import matplotlib.pyplot as plt
from mindspore import dataset as ds
from mindspore.common.initializer import Normal
from mindspore import nn
from mindspore import Tensor
from mindspore import Model
import matplotlib.pyplot as plt
import time
from IPython import display
from mindspore.ops import TensorSummary
from mindspore.train.callback import Callback
from mindspore.train.callback import SummaryCollector
from mindspore.common.initializer import Normal
from mindspore.profiler import Profiler



class ImageShowCallback(Callback):
    def __init__(self, net, eval_data):
        self.net = net
        self.eval_data = eval_data

    def step_end(self, run_context):
        plot_model_and_datasets(self.net, self.eval_data)
        display.clear_output(wait=True)

def create_dataset(num_data, batch_size=16, repeat_size=1):
    input_data = ds.GeneratorDataset(list(get_data(num_data)), column_names=['data', 'label'])
    input_data = input_data.batch(batch_size)
    input_data = input_data.repeat(repeat_size)
    return input_data

class LinearNet(nn.Cell):
    def __init__(self):
        super(LinearNet, self).__init__()
        self.fc = nn.Dense(1, 1, Normal(0.02), Normal(0.02))
        self.tensor_summary = TensorSummary()

    def construct(self, x):
        x = self.fc(x)
        self.tensor_summary("tensor", x)
        return x

def get_data(num, w=2.0, b=3.0):
    for _ in range(num):
        x = np.random.uniform(-10.0, 10.0)
        noise = np.random.normal(0, 1)
        y = x * w + b + noise
        yield np.array([x]).astype(np.float32), np.array([y]).astype(np.float32)

def plot_model_and_datasets(net, eval_data):
    weight = net.trainable_params()[0]
    bias = net.trainable_params()[1]
    x = np.arange(-10, 10, 0.1)
    y = x * Tensor(weight).asnumpy()[0][0] + Tensor(bias).asnumpy()[0]
    x1, y1 = zip(*eval_data)
    x_target = x
    y_target = x_target * 2 + 3

    plt.axis([-11, 11, -20, 25])
    plt.scatter(x1, y1, color="red", s=5)
    plt.plot(x, y, color="blue")
    plt.plot(x_target, y_target, color="green")
    plt.show()
    time.sleep(0.2)

def main():
    context.set_context(mode=context.GRAPH_MODE, device_target="CPU")
    profiler = Profiler(output_path = './summary_dir/profiler_data')
    eval_data = list(get_data(50))
    x_target_label = np.array([-10, 10, 0.1])
    y_target_label = x_target_label * 2 + 3
    x_eval_label, y_eval_label = zip(*eval_data)

    plt.scatter(x_eval_label, y_eval_label, color="red", s=5)
    plt.plot(x_target_label, y_target_label, color="green")
    plt.title("Eval data")
    plt.show()

    data_number = 1600
    batch_number = 16
    repeat_number = 1

    ds_train = create_dataset(data_number, batch_size=batch_number, repeat_size=repeat_number)
    print("The dataset size of ds_train:", ds_train.get_dataset_size())
    dict_datasets = next(ds_train.create_dict_iterator())

    print(dict_datasets.keys())
    print("The x label value shape:", dict_datasets["data"].shape)
    print("The y label value shape:", dict_datasets["label"].shape)

    net = LinearNet()
    model_params = net.trainable_params()
    for param in model_params:
        print(param, param.asnumpy())

    x_model_label = np.array([-10, 10, 0.1])
    y_model_label = (x_model_label * Tensor(model_params[0]).asnumpy()[0][0] +
                     Tensor(model_params[1]).asnumpy()[0])
    plt.axis([-10, 10, -20, 25])
    plt.scatter(x_eval_label, y_eval_label, color="red", s=5)
    plt.plot(x_model_label, y_model_label, color="blue")
    plt.plot(x_target_label, y_target_label, color="green")
    plt.show()

    net = LinearNet()
    net_loss = nn.loss.MSELoss()
    opt = nn.Momentum(net.trainable_params(), learning_rate=0.005, momentum=0.9)
    model = Model(net, net_loss, opt)

    epoch = 1
    imageshow_cb = ImageShowCallback(net, eval_data)
    collector = SummaryCollector(summary_dir='./summary_dir', collect_freq=1)
    model.train(epoch, ds_train, callbacks=[imageshow_cb, collector], dataset_sink_mode=False)

    profiler.analyse()

    plot_model_and_datasets(net, eval_data)
    for param in net.trainable_params():
        print(param, param.asnumpy())

if __name__ == "__main__":
    main()
