#include <stdio.h>
#include "graph.h"
#include <stdlib.h>
#include <limits.h>
#include "queue.h"
#include "stack.h"


void initialize_graph(Graph* graph, char* file_name) {
    if (!graph)
        return;

    FILE* file_ptr = fopen(file_name, "r");
    if (!file_ptr) {
        graph->adjacency_list = NULL;
        graph->num_vertices = 0;
        return;
    }

    int num_vertices;
    fscanf(file_ptr, "%d", &num_vertices);
    graph->num_vertices = num_vertices;
    graph->adjacency_list = (Node**)malloc(sizeof(Node*) * num_vertices);
    if (!(graph->adjacency_list)) {
        return;
    }

    for (int i = 0; i < graph->num_vertices; i++) {
        graph->adjacency_list[i] = NULL;
    }

    int weight;
    Node* new_node;
    for (int i = 0; i < num_vertices; i++) {
        for (int j = 0; j < num_vertices; j++) {
            fscanf(file_ptr, "%d", &weight);
            if (weight) {
                new_node = (Node*)malloc(sizeof(Node));
                if (!new_node) {
                    destroy_graph(graph);
                    return;
                }
                new_node->vertex = j;
                new_node->weight = weight;
                new_node->next = NULL;
                append_node(graph, i, new_node);
            }
        }
    }
    fclose(file_ptr);
    return;
}

void append_node(Graph* graph, int index, Node* new_node) {
    if (!graph || index >= graph->num_vertices)
        return;
    Node* current_node = graph->adjacency_list[index];
    if (!current_node) {
        graph->adjacency_list[index] = new_node;
    } else {
        while (current_node->next) {
            current_node = current_node->next;
        }
        current_node->next = new_node;
    }
    return;
}

void display_graph(Graph graph) {
    if (graph.num_vertices == 0)
        return;
    Node* current_node;
    for (int i = 0; i < graph.num_vertices; i++) {
        current_node = graph.adjacency_list[i];
        if (current_node) {
            while (current_node) {
                printf("Vertex 1: %d\tVertex 2: %d\tWeight: %d\n", i, current_node->vertex, current_node->weight);
                current_node = current_node->next;
            }
        } else {
            printf("\n");
        }
    }
    return;
}

void destroy_graph(Graph* graph) {
    if (!graph)
        return;
    Node* current_node;
    Node* next_node;
    for (int i = 0; i < graph->num_vertices; i++) {
        current_node = graph->adjacency_list[i];
        while (current_node) {
            next_node = current_node->next;
            free(current_node);
            current_node = next_node;
        }
        graph->adjacency_list[i] = NULL;
    }
    free(graph->adjacency_list);
    graph->adjacency_list = NULL;
    graph->num_vertices = 0;
    return;
}

SpanningTree* prims_minimum_spanning_tree(Graph graph, int start_index) {
    if (graph.num_vertices == 0) {
        SpanningTree* spanning_tree = (SpanningTree*)malloc(sizeof(SpanningTree));
        spanning_tree->spanning_tree = NULL;
        spanning_tree->size = 0;
        return spanning_tree;
    }

    if (start_index < 0 || start_index >= graph.num_vertices)
        return NULL;

    int* visited = (int*)calloc(graph.num_vertices, sizeof(int));
    if (!visited)
        return NULL;

    SpanningTree* spanning_tree = (SpanningTree*)malloc(sizeof(SpanningTree));
    if (!spanning_tree)
        return NULL;

    spanning_tree->spanning_tree = (Node**)malloc(sizeof(Node*) * graph.num_vertices);
    if (!(spanning_tree->spanning_tree)) {
        free(spanning_tree);
        return NULL;
    }

    spanning_tree->size = graph.num_vertices;
    for (int i = 0; i < graph.num_vertices; i++) {
        spanning_tree->spanning_tree[i] = NULL;
    }

    visited[start_index] = 1;
    int min_weight;
    int min_index;
    Node* current_node;
    Node* new_node;
    for (int k = 0; k < graph.num_vertices; k++) {
        min_weight = INT_MAX;
        for (int i = 0; i < graph.num_vertices; i++) {
            if (visited[i]) {
                current_node = graph.adjacency_list[i];
                while (current_node) {
                    if (!visited[current_node->vertex] && (current_node->weight < min_weight)) {
                        min_index = i;
                        min_weight = current_node->weight;
                    }
                    current_node = current_node->next;
                }
            }
        }
        if (min_weight == INT_MAX)
            break;
        else {
            new_node = (Node*)malloc(sizeof(Node));
            new_node->vertex = min_index;
            new_node->weight = min_weight;
            new_node->next = NULL;
            append_node_to_spanning_tree(spanning_tree, start_index, new_node);
            visited[min_index] = 1;
        }
    }
    free(visited);
    return spanning_tree;
}

void append_node_to_spanning_tree(SpanningTree* spanning_tree, int index, Node* new_node) {
    if (!spanning_tree || index >= spanning_tree->size)
        return;
    Node* current_node = spanning_tree->spanning_tree[index];
    if (!current_node) {
        spanning_tree->spanning_tree[index] = new_node;
    } else {
        while (current_node->next) {
            current_node = current_node->next;
        }
        current_node->next = new_node;
    }
    return;
}

void display_spanning_tree(SpanningTree spanning_tree) {
    if (spanning_tree.size == 0)
        return;
    Node* current_node;
    for (int i = 0; i < spanning_tree.size; i++) {
        current_node = spanning_tree.spanning_tree[i];
        if (current_node) {
            while (current_node) {
                printf("Vertex 1: %d\tVertex 2: %d\tWeight: %d\n", i, current_node->vertex, current_node->weight);
                current_node = current_node->next;
            }
        } else {
            printf("\n");
        }
    }
    return;
}

void breadth_first_search(Graph graph, int start_index) {
    if (graph.num_vertices == 0)
        return;
    Queue queue;
    initialize_queue(&queue);
    int* visited = (int*)calloc(graph.num_vertices, sizeof(int));
    if (!visited)
        return;
    visited[start_index] = 1;
    enqueue(&queue, start_index);
    int index;
    Node* current_node;
    while (!is_empty(queue)) {
        index = dequeue(&queue);
        printf("%d ", index);
        current_node = graph.adjacency_list[index];
        while (current_node) {
            if (!visited[current_node->vertex]) {
                enqueue(&queue, current_node->vertex);
                visited[current_node->vertex] = 1;
            }
            current_node = current_node->next;
        }
    }
    printf("\n");
    return;
}

void depth_first_search(Graph graph, int start_index) {
    if (graph.num_vertices == 0)
        return;
    Stack stack;
    initialize_stack(&stack);
    int* visited = (int*)calloc(graph.num_vertices, sizeof(int));
    if (!visited)
        return;
    visited[start_index] = 1;
    push(&stack, start_index);
    int index;
    Node* current_node;
    while (!is_empty(stack)) {
        index = pop(&stack);
        printf("%d ", index);
        current_node = graph.adjacency_list[index];
        while (current_node) {
            if (!visited[current_node->vertex]) {
                push(&stack, current_node->vertex);
                visited[current_node->vertex] = 1;
            }
            current_node = current_node->next;
        }
    }
    printf("\n");
    return;
}

