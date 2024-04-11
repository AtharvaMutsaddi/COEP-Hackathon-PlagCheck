#include <stdio.h>
#include "graph.h"
#include <stdlib.h>
#include <limits.h>
#include "queue.h"
#include "stack.h"

void graph_init(graph *g, char *file_name){
	if(!g)
		return;

	FILE *fptr = fopen(file_name, "r");

	if(!fptr){
		g->arr = NULL;
		g->size = 0;
		return;
	}

	int s;
	fscanf(fptr, "%d", &s);//taking the no. of the vertices in the graph.
			       
	g->arr = (node **)malloc(sizeof(node *) * s);
	if(!(g->arr)){
		return;
	}
	g->size = s;

	for(int i = 0; i < g->size; i++){
		g->arr[i] = NULL;
	}

	int w;
	node *nn;
	for(int i = 0; i < s; i++){
		for(int j = 0; j < s; j++){
			fscanf(fptr, "%d", &w);
			if(w){
				nn = (node *)malloc(sizeof(node));
				if(!nn){
					destroy_graph(g);
					return;
				}
				nn->v = j;
				nn->w = w;
				nn->next = NULL;
				append_node(g, i, nn);
			}
		}
	}
	fclose(fptr);
	return;
}

void append_node(graph *g, int i, node *nn){
	if(!g)
		return;
	if(i >= g->size)
		return;
	node *pi = g->arr[i];
	if(!pi){
		g->arr[i] = nn;
	}
	else{
		while(pi->next){
			pi = pi->next;
		}
		pi->next = nn;
	}
	return;
}

void display_graph(graph g){
	if(g.size == 0)
		return;
	int w;
	int j;
	node *n;
	for(int i = 0; i < g.size; i++){
		n = g.arr[i];
		if(n){
			while(n){
				printf("v1 - %d\tv2 - %d\tweight - %d\n", i, n->v, n->w);
				n = n->next;
			}
		}
		else{
			printf("\n");
		}
	}
	return;
}

void destroy_graph(graph *g){
	if(!g)
		return;
	node *n, *nextn;
	for(int i = 0; i < g->size; i++){
		n = g->arr[i];
		while(n){
			nextn = n->next;
			free(n);
			n = nextn;
		}
		g->arr[i] = NULL;
	}
	free(g->arr);
	g->arr = NULL;
	g->size = 0;
	return;
}

ST *primsMinST(graph g,int sind){
	if(g.size == 0){
		ST *st = (ST *)malloc(sizeof(ST));
		st->arr = NULL;
		st->size = 0;
		return st;
	}

	if((sind < 0) || (sind >= g.size))
		return NULL;
	int *visited = (int *)calloc(g.size, sizeof(int));
	if(!visited)
		return NULL;
	ST *st;
	st = (ST *)malloc(sizeof(ST));
	if(!st)
		return NULL;
	st->arr = (node **)malloc(sizeof(node *) * g.size);
	if(!(st->arr)){
		free(st);
		return NULL;
	}
	st->size = g.size;
	for(int i = 0; i < g.size; i++){
		st->arr[i] = NULL;
	}

	visited[sind] = 1;
	int wmin;
	int imin;
	int jmin;
	node *p;
	node *nn;
	for(int k = 0; k < g.size; k++){
		wmin = INT_MAX;
		for(int i = 0; i < g.size; i++){
			if(visited[i]){
				p = g.arr[i];
				while(p){
					if(!visited[p->v] && (p->w < wmin)){
						imin = i;
						jmin = p->v;
						wmin = p->w;
					}
					p = p->next;
				}
			}
		}
		if(wmin == INT_MAX)
			break;
		else{
			nn = (node *)malloc(sizeof(node));
			nn->v = jmin;
			nn->w = wmin;
			nn->next = NULL;
			ST_append_node(st, imin, nn);
			nn = (node *)malloc(sizeof(node));
			nn->v = imin;
			nn->w = wmin;
			nn->next = NULL;
			ST_append_node(st, jmin, nn);	
			visited[jmin] = 1;
		}

	}
	return st;
}

void ST_init(ST *st){
	if(!st)
		return;
	st->arr = NULL;
	st->size = 0;
	return;
}

void ST_append_node(ST *st, int i, node *nn){
	if(!st)
		return;
	if(i >= st->size)
		return;
	node *pi = st->arr[i];
	if(!pi){
		st->arr[i] = nn;
	}
	else{
		while(pi->next){
			pi = pi->next;
		}
		pi->next = nn;
	}
	return;
}

void display_ST(ST st){
	if(st.size == 0)
		return;
	node *n;
	for(int i = 0; i < st.size; i++){
		n = st.arr[i];
		if(n){
			while(n){
				printf("v1 - %d\tv2 - %d\tweight - %d\n", i, n->v, n->w);
				n = n->next;
			}
		}
		else{
			printf("\n");
		}
	}
	return;
}

void BFS_traversal(graph g, int sind){
	queue q;
	initQ(&q);
	int *visited = (int *)calloc(g.size, sizeof(int));
	if(!visited)
		return;
	visited[sind] = 1;
	enqueueQ(&q, sind);
	int i;
	node *n;
	while(!isEmptyQ(q)){
		i = dequeueQ(&q);
		printf("%d ", i);
		n = g.arr[i];
		while(n){
			if(!visited[n->v]){
				enqueueQ(&q, n->v);
				visited[n->v] = 1;
			}
			n = n->next;
		}
	}
	printf("\n");
}
void DFS_traversal(graph g, int sind){
	stack s;
	init(&s);
	int *visited = (int *)calloc(g.size, sizeof(int));
	if(!visited)
		return;
	visited[sind] = 1;
	push(&s, sind);
	int i;
	node *n;
	while(!isEmpty(s)){
		i = pop(&s);
		printf("%d ", i);
		n = g.arr[i];
		while(n){
			if(!visited[n->v]){
				push(&s, n->v);
				visited[n->v] = 1;
			}
			n = n->next;
		}
	}
	printf("\n");
}
