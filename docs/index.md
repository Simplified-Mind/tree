!!! abstract
::: tree

!!! info "Features"
* [x] Reactive 
* [x] Symbolic
* [x] Read only
* [x] Dynamic expression validation and execution
* [x] Dynamic tree builder


!!! example "Diagram"
```mermaid
graph LR
    A[A] --> B[B]
    A --> C{C}
    C{C} --> D((D))
    C --> E((E))
    
    X[X] --> Y[Y]
    X --> Z(Z)
    Z(Z) --> D((D))
    Z --> E((E))
```

!!! todo "TODO"
- [ ] Features
  * [ ] Async/Thread support
  * [ ] Echarts utilities
  * [ ] Vxe-table utilities
- [ ] UI
    * [ ] Tree builder 
    * [ ] Node builder with formula 
    * [ ] Tree viewer with expandable grid editor
