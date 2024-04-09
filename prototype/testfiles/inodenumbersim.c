#define _LARGEFILE64_SOURCE /* See feature_test_macros(7) */
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <linux/fs.h>
#include <math.h>
#include <time.h>
#include "ext2_fs.h"
#define SUPERBLOCK_OFFSET 1024

int block_size;
int fd;

void print_time(long time_stamp)
{
    struct tm *tstamp = localtime(&time_stamp);
    char buffer[26];
    strftime(buffer, 26, "%Y-%m-%d %H:%M:%S", tstamp);
    printf("Timestamp: %s\n", buffer);
}

void read_indirect_block(unsigned int block_num)
{
    lseek64(fd, block_size * block_num, SEEK_SET);
    int num_indirect_blocks = block_size / sizeof(int);
    int indirect_blocks[num_indirect_blocks];
    read(fd, indirect_blocks, block_size);
    for (int i = 0; i < num_indirect_blocks; i++)
    {
        if (indirect_blocks[i] != 0)
        {
            printf("%d, ", indirect_blocks[i]);
        }
    }
}

void read_double_indirect_block(unsigned int block_num){
    lseek64(fd, block_size * block_num, SEEK_SET);
    int num_double_indirect_blocks = block_size / sizeof(int);
    int indirect_double_blocks[num_double_indirect_blocks];
    read(fd, indirect_double_blocks, block_size);
    for (int i = 0; i < num_double_indirect_blocks; i++)
    {
        if (indirect_double_blocks[i] != 0)
        {
            read_indirect_block(indirect_double_blocks[i]);
        }
    } 
}

void read_triple_indirect_block(unsigned int block_num){
    lseek64(fd, block_size * block_num, SEEK_SET);
    int num_triple_indirect_blocks = block_size / sizeof(int);
    int indirect_triple_blocks[num_triple_indirect_blocks];
    read(fd, indirect_triple_blocks, block_size);
    for (int i = 0; i < num_triple_indirect_blocks; i++)
    {
        if (indirect_triple_blocks[i] != 0)
        {
            read_double_indirect_block(indirect_triple_blocks[i]);
        }
    } 
}

int main(int argc, char *argv[])
{
    if (argc != 3)
    {
        printf("Usage: %s <device file name> <inode number>", argv[0]);
    }
    char *dev_file_name = argv[1];
    int inode_num = atoi(argv[2]);
    fd = open(dev_file_name, O_RDONLY);
    if (fd < 0)
    {
        perror("file read:");
        exit(1);
    }
    lseek64(fd, SUPERBLOCK_OFFSET, SEEK_SET);
    struct ext2_super_block super_block;
    struct ext2_group_desc group_desc;
    int cnt = read(fd, &super_block, sizeof(struct ext2_super_block));
    if (cnt < sizeof(struct ext2_super_block))
    {
        printf("Read of super block unsuccessful\n");
        exit(1);
    }
    block_size = 1024 << super_block.s_log_block_size;
    printf("Block size:%d\n", block_size);
    int block_group_num = (inode_num - 1) / super_block.s_inodes_per_group;
    int group_desc_tables = ((SUPERBLOCK_OFFSET + sizeof(struct ext2_super_block)) / block_size);
    if (((SUPERBLOCK_OFFSET + sizeof(struct ext2_super_block)) % block_size) > 0)
    {
        group_desc_tables += 1;
    }
    int bgno = (inode_num - 1) / super_block.s_inodes_per_group;
    lseek64(fd, group_desc_tables * block_size + (sizeof(struct ext2_group_desc) * bgno), SEEK_SET);
    cnt = read(fd, &group_desc, sizeof(struct ext2_group_desc));
    if (cnt < sizeof(struct ext2_group_desc))
    {
        printf("Read of group descriptor unsuccessful:\n");
        exit(1);
    }
    struct ext2_inode inode;
    printf("Inode Table: %d\n", group_desc.bg_inode_table);
    int index = (inode_num - 1) % super_block.s_inodes_per_group;
    int inode_size = super_block.s_inode_size;
    int inode_offset = group_desc.bg_inode_table * block_size + index * inode_size;
    lseek64(fd, inode_offset, SEEK_SET);
    read(fd, &inode, sizeof(struct ext2_inode));
    printf("Size: %d \n", inode.i_size);
    printf("Group Number:%d\n", bgno);
    printf("File ACL:%d\n", inode.i_file_acl);
    printf("Links Count:%d\n", inode.i_links_count);
    printf("Access Time: ");
    print_time(inode.i_atime);
    printf("Inode change time: ");
    print_time(inode.i_ctime);
    printf("Modification time: ");
    print_time(inode.i_mtime);
    printf("Number of blocks: %d\n", inode.i_blocks);
    printf("\n------------------\nBlocks:\n");
    struct ext2_dir_entry_2 dir_entry;
    printf("Direct Blocks: ");
    for (int i = 0; i < 12; i++)
    {

        if (inode.i_block[i] != 0)
        {
            printf("%d, ", inode.i_block[i]);
        }
    }
    if (inode.i_block[12] != 0)
    {
        printf("\nSingly Indirect Block: ");
        read_indirect_block(inode.i_block[12]);
    }
    if (inode.i_block[13] != 0)
    {
        printf("\nDoubly Indirect Block: ");
        read_double_indirect_block(inode.i_block[13]);
    }
    if (inode.i_block[14] = 0)
    {
        printf("\nTriply Indirect Block: ");
        read_triple_indirect_block(inode.i_block[14]);
    }
    close(fd);
    return 0;
}
