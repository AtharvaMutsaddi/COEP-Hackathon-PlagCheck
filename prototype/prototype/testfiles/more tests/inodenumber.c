#define _LARGEFILE64_SOURCE     /* See feature_test_macros(7) */
#include <sys/types.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <linux/fs.h>
#include <time.h>
#include <string.h>
#include <time.h>

#include <ext2fs/ext2_fs.h>
//#include "ext2_fs.h"

void my_printf(long time);

int main(int argc, char *argv[]) {
	int fd;
	int count;
	int first_indirect_count;
	int ino, i;
	int bgno, iindex, inode_size, block_size;
	unsigned long inode_offset;
	struct ext2_super_block sb; 
	struct ext2_inode inode; 
	struct ext2_group_desc bgdesc;

	ino = atoi(argv[2]);
        fd = open(argv[1], O_RDONLY); 
	if(fd == -1) {
		perror("readsuper:");
		exit(errno);
	}

	lseek64(fd, 1024, SEEK_CUR);
	printf("size of super block = %lu\n", sizeof(struct ext2_super_block));
	count = read(fd, &sb, sizeof(struct ext2_super_block));
	printf("Magic: %x\n", sb.s_magic);
	printf("Inodes Count: %d\n", sb.s_inodes_count);
	printf("size of BG DESC = %lu\n", sizeof(struct ext2_group_desc));
	inode_size = sb.s_inode_size;
	block_size = 1024 << sb.s_log_block_size;

	bgno = (ino -1) / sb.s_inodes_per_group;
	iindex = (ino -1) % sb.s_inodes_per_group;
	int block_group_size = sb.s_blocks_per_group * sb.s_log_block_size;
	if (block_size==1024) {
		lseek64(fd,1024+block_size+bgno*sizeof(bgdesc),SEEK_SET);
	}
	else {
		lseek64(fd, block_size + bgno * sizeof(block_group_size), SEEK_SET);
	}
	count = read(fd, &bgdesc, sizeof(struct ext2_group_desc));
	printf("Inode Table: %d\n", bgdesc.bg_inode_table); 

	inode_offset = bgdesc.bg_inode_table  * block_size + iindex * inode_size; 
	lseek64(fd, inode_offset, SEEK_SET);
	read(fd, &inode, sizeof(inode));	
	printf("size of file %d \n", inode.i_size);
	printf("Mode:%04o\n",inode.i_mode & 0777);
	printf("Access Time:\n");
	my_printf(inode.i_atime);
	printf("Creation Time:\n");
	my_printf(inode.i_ctime);
	printf("Modification Time:\n");
	my_printf(inode.i_mtime);
	printf(" number of blocks %d , blocks: ", inode.i_blocks);
	for(i = 0; i < inode.i_blocks; i++) {
		if (inode.i_block[i]==0) {
			break;
		}
		if (i>=0 && i<12) {
			printf("%d, ", inode.i_block[i]);
		}
		else if (i==12) {
			printf("First indirect block:%d and blocks are\n",inode.i_block[i]);
			int first_indirect_entry = inode.i_block[i];
			lseek64(fd, first_indirect_entry*block_size,SEEK_SET);

			//at the first indirectly pointed position
			
			int arr[block_size/sizeof(int)];
			first_indirect_count = read(fd,arr,block_size);

			int j=0;
			while (j<first_indirect_count/sizeof(int)) {
				if (arr[j]==0) {
					break;
				}
				printf("%d,",arr[j]);
				j++;
			}
			printf("\n"); 
		}
		else if (i==13) {
			int second_indirect_entry = inode.i_block[13];
			lseek(fd,second_indirect_entry*block_size,SEEK_SET);

			//at the arr pointed at that location
			int arr[block_size/sizeof(int)];
			int second_indirect_count = read(fd,arr,block_size);
			
			for (int j=0;j<second_indirect_count/sizeof(int);j++) {
				if (arr[j]==0) {
					break;
				}
				int intermediate_block = arr[j];
				lseek64(fd,intermediate_block*block_size,SEEK_SET);
				
				int arr1[block_size/sizeof(int)];
				int first_indirect_count1 = read(fd,arr1,block_size);

				for (int k=0;k<first_indirect_count1/sizeof(int);k++) {
					if (arr1[k]==0) {
						break;
					}
					printf("%d",arr1[k]);
				}
				printf("\n");
			}
		}

		else if (i==14) {
			int triple_indirect_entry = inode.i_block[i];
			lseek64(fd,triple_indirect_entry*block_size,SEEK_SET);

			int arr[block_size/sizeof(int)];
			int triple_indirect_count = read(fd,arr,block_size);

			for (int j=0;j<triple_indirect_count/sizeof(int);j++) {
				if (arr[j]==0) {
					break;
				}
				int intermediate_entry = arr[j];
				lseek64(fd,intermediate_entry*block_size,SEEK_SET);

				int arr1[block_size/sizeof(int)];
				int triple_indirect_count1 = read(fd,arr1,block_size);
				for (int k=0;k<triple_indirect_count1/sizeof(int);k++) {
					if (arr1[k]==0) {
						break;
					}
					int intermediate_entry1 = arr1[k];
					lseek64(fd,intermediate_entry1*block_size,SEEK_SET);

					int arr2[block_size/sizeof(int)];
					int triple_indirect_count2 = read(fd,arr2,block_size);

					for (int l=0;l<triple_indirect_count2/sizeof(int);l++) {
						if (arr2[l]==0) {
							break;
						}
						printf("%d",arr2[l]);
					}
				}
			}
			printf("\n");
		}
	}
	close(fd); 
}

//warning in int time ? 
void my_printf(long time) {     
	struct tm* stored_time;
	stored_time = localtime(&time);
	char time_str[75];
	strftime(time_str,75,"Local time and date: %Y-%m-%d %H:%M:%S",stored_time);  //format in suitable type and then print
	printf("%s\n",time_str);

}
