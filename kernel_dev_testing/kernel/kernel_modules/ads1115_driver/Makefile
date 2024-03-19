ifneq ($(KERNELRELEASE),)
obj-m := adc1115.o
else
KDIR := /compulab_kernel/build/

all:
	$(MAKE) -C $(KDIR) M=$(PWD)
endif
