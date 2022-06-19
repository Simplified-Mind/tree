!!! abstract
::: tree

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
- [x] Reactive node
- [ ] User interface
    * [ ] Tree builder 
    * [ ] Node builder with formula 
    * [ ] Tree viewer with expandable grid editor
