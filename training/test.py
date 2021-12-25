from torch import nn
from torch.autograd import Variable
import torch
import os 

os.environ['CUDA_LAUNCH_BLOCKING'] = "1"
DEVICE_IDS=[3,5,6,7]
os.environ['CUDA_VISIBLE_DEVICES']=",".join(list(map(str,DEVICE_IDS)))
 
l = nn.Linear(5,5).cuda()
pl = nn.DataParallel(l)
print("Checkpoint 1")
a = Variable(torch.rand(5,5).cuda(), requires_grad=True)
print("Checkpoint 2")
print(pl(a)) # Here it gets stuck