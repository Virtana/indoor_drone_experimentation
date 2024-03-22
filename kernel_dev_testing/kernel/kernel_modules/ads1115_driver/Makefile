ifneq ($(KERNELRELEASE),)
obj-m := adc1115.o
else
# Specifying this dir requires installing linux headers
KDIR := /compulab_kernel/build/

all:
	$(MAKE) -C $(KDIR) M=$(PWD)
endif
