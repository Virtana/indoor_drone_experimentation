#include <linux/i2c.h>
#include <linux/module.h>
#include <linux/delay.h>

static const struct i2c_device_id adc1115_i2c_id[] = {
    {"adc1115", 0x1115c},
    { }
};

MODULE_DEVICE_TABLE(i2c, adc1115_i2c_id);

static const struct of_device_id adc1115_of_match[] = {
    {.compatible = "adc, adc1115"},
    { }
};

MODULE_DEVICE_TABLE(of, adc1115_of_match);

static int adc1115_probe(struct i2c_client *client, const struct i2c_device_id *id)
{
    //uint8_t addr = 0x48;
    //char rec_mode = addr << 1;
    //char tra_mode = (addr << 1) | 1;
    //uint16_t set_mode_os = 0x8583;
    //uint8_t set_mode_os_h = (uint8_t)(set_mode_os >> 8);
    //uint8_t set_mode_os_l = (uint8_t)(set_mode_os & 0xFF);
    //char start_conv[] = {rec_mode, 0x01, 0x85, 0x83};
    //char read_conv[] = {tra_mode, 0x00};

    char start_conv[] = {0x01, 0xC5, 0x83};
    char read_conv[] = {0x00};


    uint8_t conv[2] = {1,1};
    int ret = 0;

    printk("ADC1115 PROBE\n");

    i2c_master_send(client, start_conv, 3);
    mdelay(20);

    i2c_master_send(client, read_conv, 1);
    ret = i2c_master_recv(client, conv, 2);

    if (ret > 0)
    {
        printk("%x %x\n", conv[0], conv[1]);
    }else
    {
        printk("REC error\n");
    }

    return 0;
}

static void adc1115_remove(struct i2c_client *client)
{
    printk("ADC1115 REMOVE\n");
}


static struct i2c_driver adc1115_i2c_driver = {
    .driver = {
        .name = "adc1115_i2c",
        .of_match_table = adc1115_of_match,
    },
    .probe = adc1115_probe,
    .remove = adc1115_remove,
    .id_table = adc1115_i2c_id,
};

module_i2c_driver(adc1115_i2c_driver);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("ADS1115 DRIVER");
MODULE_AUTHOR("ADS1115 AUTHOR");
