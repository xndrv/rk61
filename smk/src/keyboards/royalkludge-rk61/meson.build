kb_dir = meson.current_source_dir()

keyboards += {
    'royalkludge-rk61' : {
        'dir' : kb_dir,
        'platform' : 'sh68f90',
        'src' : files('user_init.c', 'user_matrix.c', 'user_sleep.c', 'kb.c'),
        'layouts' : {
            'default' : {
                'dir' : kb_dir / 'layouts/default',
                'src' : files('layouts/default/layout.c'),
            },
            'led-test' : {
                'dir' : kb_dir / 'layouts/led-test',
                'src' : files('layouts/led-test/layout.c', 'layouts/led-test/indicators.c'),
            },
        },
        'options' : {
            'vendor_id' : '0x258a',
            'product_id' : '0x00e1',
            'manufacturer' : 'Royal Kludge',
            'product' : 'RK61 SMK prototype',
        },
    },
    'royalkludge-rk61-rf-test' : {
        'args' : ['-DUSB_START_WITHOUT_ENUM_WAIT'],
        'dir' : kb_dir,
        'platform' : 'sh68f90',
        'src' : files(
            'user_init.c', 'user_matrix.c', 'user_sleep.c',
            'layouts/rf-test/kb.c', 'layouts/rf-test/radio.c', 'layouts/rf-test/packet.c',
            'layouts/rf-test/battery.c',
        ),
        'layouts' : {
            'default' : {
                'dir' : kb_dir / 'layouts/rf-test',
                'src' : files('layouts/rf-test/layout.c', 'layouts/rf-test/lighting.c', 'layouts/led-test/indicators.c'),
            },
        },
        'options' : {
            'vendor_id' : '0x258a',
            'product_id' : '0x00e1',
            'manufacturer' : 'Royal Kludge',
            'product' : 'RK61 SMK wireless test',
        },
    },
}
