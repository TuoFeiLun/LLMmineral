import { useState } from 'react';
import {
    IconMessageCircle,
    IconDatabase,
    IconUpload,
    IconDiamond,
} from '@tabler/icons-react';
import { Center, Stack, Tooltip, UnstyledButton, Text } from '@mantine/core';
import classes from './Navbar.module.css';

function NavbarLink({ icon: Icon, label, active, onClick }) {
    return (
        <Tooltip label={label} position="right" transitionProps={{ duration: 0 }}>
            <UnstyledButton onClick={onClick} className={classes.link} data-active={active || undefined}>
                <Icon size={20} stroke={1.5} />
            </UnstyledButton>
        </Tooltip>
    );
}

const navigationItems = [
    { key: 'chat', icon: IconMessageCircle, label: 'Chat' },
    { key: 'collections', icon: IconDatabase, label: 'Collections' },
    { key: 'upload', icon: IconUpload, label: 'Upload Files' },
];

export function Navbar({ activeView, setActiveView }) {
    const links = navigationItems.map((item) => (
        <NavbarLink
            {...item}
            key={item.key}
            active={item.key === activeView}
            onClick={() => setActiveView(item.key)}
        />
    ));

    return (
        <nav className={classes.navbar}>
            <Center>
                <Stack align="center" gap={4}>
                    <IconDiamond size={30} stroke={1.5} />
                    <Text size="xs" fw={500} c="dimmed">
                        IFN712
                    </Text>
                </Stack>
            </Center>

            <div className={classes.navbarMain}>
                <Stack justify="center" gap={0}>
                    {links}
                </Stack>
            </div>

            <Stack justify="center" gap={0}>
                <Text size="xs" c="dimmed" ta="center">
                    Mineral Explorer
                </Text>
            </Stack>
        </nav>
    );
}
